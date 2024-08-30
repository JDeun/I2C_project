from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import ssl
from typing import Dict, Any, Tuple
import logging

class ImageMetadataProcessor:
    def __init__(self):
        """
        ImageMetadataProcessor 클래스 초기화
        지오코더를 생성하고 로거를 설정합니다.
        """
        self.geolocator = self._create_geolocator()
        self.logger = logging.getLogger(__name__)

    def process(self, image_path: str) -> Dict[str, Any]:
        """
        이미지의 메타데이터를 처리합니다.
        
        :param image_path: 처리할 이미지의 경로
        :return: 추출된 EXIF 데이터와 위치 정보를 포함한 딕셔너리
        """
        self.logger.info(f"{image_path}에서 메타데이터 추출 중")
        exif_data = self._get_exif_data(image_path)
        labeled_exif = self._get_labeled_exif(exif_data)
        location_info = self._get_location_info(labeled_exif)
        return {
            'exif_data': self._serialize_exif(exif_data),
            'labeled_exif': labeled_exif,
            'location_info': location_info
        }

    def _serialize_exif(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
            """
            EXIF 데이터를 JSON 직렬화 가능한 형태로 변환합니다.
            
            :param exif_data: 원본 EXIF 데이터
            :return: 직렬화된 EXIF 데이터
            """
            serialized = {}
            for key, value in exif_data.items():
                if isinstance(value, dict):
                    serialized[key] = self._serialize_exif(value)
                elif isinstance(value, (tuple, list)):
                    serialized[key] = [self._serialize_value(v) for v in value]
                else:
                    serialized[key] = self._serialize_value(value)
            return serialized

    def _serialize_value(self, value: Any) -> Any:
        """
        단일 EXIF 값을 직렬화합니다.
        
        :param value: 직렬화할 값
        :return: 직렬화된 값
        """
        if isinstance(value, Image.Exif):
            return self._serialize_exif(dict(value))
        elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
            return float(value)
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='replace')
        return str(value)

    def _create_geolocator(self) -> Nominatim:
        """
        SSL 인증서 검증을 비활성화한 Nominatim 지오코더를 생성합니다.
        
        :return: 설정된 Nominatim 객체
        """
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return Nominatim(user_agent="my_app", ssl_context=ctx)

    def _get_exif_data(self, image_path: str) -> Dict[str, Any]:
        """
        이미지에서 EXIF 데이터를 추출합니다.
        
        :param image_path: EXIF 데이터를 추출할 이미지의 경로
        :return: 추출된 EXIF 데이터
        """
        exif_data = {}
        try:
            with Image.open(image_path) as image:
                info = image._getexif()
                if info:
                    exif_data = self._process_exif_info(info)
        except Exception as e:
            self.logger.error(f"EXIF 데이터 추출 중 오류 발생: {e}")
        return exif_data

    def _process_exif_info(self, info: Dict[int, Any]) -> Dict[str, Any]:
        """
        EXIF 정보를 처리합니다.
        
        :param info: 원시 EXIF 정보
        :return: 처리된 EXIF 데이터
        """
        exif_data = {}
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                exif_data[decoded] = self._process_gps_info(value)
            else:
                exif_data[decoded] = value
        return exif_data

    def _process_gps_info(self, value: Dict[int, Any]) -> Dict[str, Any]:
        """
        GPS 정보를 처리합니다.
        
        :param value: 원시 GPS 정보
        :return: 처리된 GPS 데이터
        """
        gps_data = {}
        for t in value:
            sub_decoded = GPSTAGS.get(t, t)
            gps_data[sub_decoded] = value[t]
        return gps_data

    def _get_labeled_exif(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        EXIF 데이터에 레이블을 추가합니다.
        
        :param exif_data: 원시 EXIF 데이터
        :return: 레이블이 추가된 EXIF 데이터
        """
        labeled_exif = {}
        labeled_exif["Date/Time"] = exif_data.get("DateTimeOriginal", "N/A")
        
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            labeled_exif.update(self._extract_gps_coordinates(gps_info))
        
        return labeled_exif

    def _extract_gps_coordinates(self, gps_info: Dict[str, Any]) -> Dict[str, float]:
        """
        GPS 정보에서 위도와 경도를 추출합니다.
        
        :param gps_info: GPS 정보
        :return: 위도와 경도를 포함한 딕셔너리
        """
        lat = self._convert_to_degrees(gps_info.get("GPSLatitude", [0, 0, 0]))
        lon = self._convert_to_degrees(gps_info.get("GPSLongitude", [0, 0, 0]))
        if gps_info.get("GPSLatitudeRef", "N") != "N":
            lat = -lat
        if gps_info.get("GPSLongitudeRef", "E") != "E":
            lon = -lon
        return {"Latitude": lat, "Longitude": lon}

    @staticmethod
    def _convert_to_degrees(value: Tuple[float, float, float]) -> float:
        """
        GPS 좌표를 도(degree) 단위로 변환합니다.
        
        :param value: (도, 분, 초) 형식의 GPS 좌표
        :return: 도 단위로 변환된 GPS 좌표
        """
        if not value:
            return 0
        d, m, s = [float(x) for x in value]
        return d + (m / 60.0) + (s / 3600.0)

    def _get_location_info(self, labeled_exif: Dict[str, Any]) -> Dict[str, str]:
        """
        GPS 좌표를 이용해 위치 정보를 가져옵니다.
        
        :param labeled_exif: 레이블이 추가된 EXIF 데이터
        :return: 위치 정보를 포함한 딕셔너리
        """
        location_info = {}
        if "Latitude" in labeled_exif and "Longitude" in labeled_exif:
            try:
                location = self._reverse_geocode(labeled_exif['Latitude'], labeled_exif['Longitude'])
                if location:
                    location_info = self._extract_address_components(location)
            except GeocoderTimedOut:
                self.logger.warning("지오코딩 서비스 시간 초과. 다시 시도해주세요.")
            except Exception as e:
                self.logger.error(f"위치 정보를 가져오는 데 실패했습니다: {e}")
        return location_info

    def _reverse_geocode(self, lat: float, lon: float) -> Any:
        """
        위도와 경도를 이용해 역지오코딩을 수행합니다.
        
        :param lat: 위도
        :param lon: 경도
        :return: 역지오코딩 결과
        """
        return self.geolocator.reverse(f"{lat}, {lon}")

    def _extract_address_components(self, location: Any) -> Dict[str, str]:
        """
        위치 정보에서 주소 구성 요소를 추출합니다.
        
        :param location: 역지오코딩 결과
        :return: 주소 구성 요소를 포함한 딕셔너리
        """
        address = location.raw['address']
        return {
            "full_address": location.address,
            "country": address.get('country', ''),
            "state": address.get('state', ''),
            "city": address.get('city', address.get('town', address.get('village', ''))),
            "suburb": address.get('suburb', ''),
            "road": address.get('road', ''),
            "house_number": address.get('house_number', ''),
            "postcode": address.get('postcode', '')
        }