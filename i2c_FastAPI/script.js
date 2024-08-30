// DOM 요소 선택
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const mobileOptions = document.getElementById('mobileOptions');
const selectFileButton = document.getElementById('selectFileButton');
const captureButton = document.getElementById('captureButton');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const generateCaptionsButton = document.getElementById('generateCaptions');
const captionCarousel = document.getElementById('captionCarousel');
const writeOptions = document.getElementById('writeOptions');
const generateContentButton = document.getElementById('generateContent');
const generatedContent = document.getElementById('generatedContent');
const contentSkeleton = document.getElementById('contentSkeleton');
const content = document.getElementById('content');
const hashtags = document.getElementById('hashtags');
const copyContentButton = document.getElementById('copyContent');
const shareOptions = document.getElementById('shareOptions');
const userAgeSelect = document.getElementById('userAge');
const addMoreImagesButton = document.getElementById('addMoreImages');

// API 기본 URL 설정
const API_BASE_URL = 'http://localhost:8000';

// 나이 선택 옵션 생성
for (let i = 99; i >= 0; i--) {
    const option = document.createElement('option');
    option.value = i;
    option.textContent = i;
    userAgeSelect.appendChild(option);
}

// 모바일 환경 감지
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

if (isMobile) {
    dropzone.addEventListener('click', () => {
        mobileOptions.style.display = 'block';
    });

    selectFileButton.addEventListener('click', () => {
        fileInput.click();
    });

    captureButton.addEventListener('click', () => {
        if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    // 여기에 카메라 스트림 처리 로직 추가
                    console.log('Camera accessed');
                })
                .catch((error) => {
                    console.error('Camera access error:', error);
                });
        }
    });
} else {
    dropzone.addEventListener('click', () => fileInput.click());
}

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

let uploadedImages = [];

function handleFiles(files) {
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            addImagePreview(file, e.target.result);
        };
        reader.readAsDataURL(file);
    });
    generateCaptionsButton.style.display = 'block';
}

function addImagePreview(file, preview) {
    const imageContainer = document.createElement('div');
    imageContainer.className = 'imagePreview';
    
    const img = document.createElement('img');
    img.src = preview;
    
    const removeButton = document.createElement('button');
    removeButton.textContent = 'X';
    removeButton.className = 'removeImage';
    removeButton.addEventListener('click', () => removeImage(imageContainer, file));
    
    imageContainer.appendChild(img);
    imageContainer.appendChild(removeButton);
    imagePreviewContainer.appendChild(imageContainer);
    
    uploadedImages.push({
        file: file,
        preview: preview,
        container: imageContainer
    });
}

function removeImage(container, file) {
    container.remove();
    uploadedImages = uploadedImages.filter(img => img.file !== file);
    if (uploadedImages.length === 0) {
        generateCaptionsButton.style.display = 'none';
    }
}

// 글쓰기 스타일과 톤 불러오기
async function loadWritingStylesAndTones() {
    try {
        const stylesResponse = await fetch(`${API_BASE_URL}/writing-styles/`);
        const tonesResponse = await fetch(`${API_BASE_URL}/writing-tones/`);
        
        const stylesData = await stylesResponse.json();
        const tonesData = await tonesResponse.json();

        const writingStyleSelect = document.getElementById('writingStyle');
        const writingToneSelect = document.getElementById('writingTone');

        stylesData.styles.forEach(style => {
            const option = document.createElement('option');
            option.value = style;
            option.textContent = style;
            writingStyleSelect.appendChild(option);
        });

        Object.entries(tonesData.tones).forEach(([key, value]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            writingToneSelect.appendChild(option);
        });
    } catch (error) {
        console.error('글쓰기 스타일과 톤을 불러오는 중 오류 발생:', error);
    }
}

// 페이지 로드 시 글쓰기 스타일과 톤 불러오기
window.addEventListener('load', loadWritingStylesAndTones);

// 이미지 업로드 함수
async function uploadImages(files) {
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/upload-images/`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        return data.image_data;
    } catch (error) {
        console.error('이미지 업로드 중 오류 발생:', error);
        throw error;
    }
}

// 컨텐츠 생성 함수
async function generateContent(imageDataList, userContext, writingStyle, writingTone, writingLength, temperature, userInfo) {
    const formData = new FormData();
    formData.append('image_data_list', JSON.stringify(imageDataList));
    formData.append('user_context', userContext);
    formData.append('writing_style', writingStyle);
    formData.append('writing_tone', writingTone);
    formData.append('writing_length', writingLength);
    formData.append('temperature', temperature);
    formData.append('user_info', JSON.stringify(userInfo));

    console.log('Sending image data:', imageDataList);  // 로그 추가

    try {
        const response = await fetch(`${API_BASE_URL}/generate-content/`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    } catch (error) {
        console.error('컨텐츠 생성 중 오류 발생:', error);
        throw error;
    }
}

generateCaptionsButton.addEventListener('click', async () => {
    generateCaptionsButton.disabled = true;
    try {
        const imageData = await uploadImages(uploadedImages.map(img => img.file));
        displayCaptions(imageData);
    } catch (error) {
        alert('이미지 캡션 생성 중 오류가 발생했습니다.');
    } finally {
        generateCaptionsButton.disabled = false;
    }
});

function displayCaptions(captions) {
    captionCarousel.innerHTML = '';
    captions.forEach((caption, index) => {
        const card = document.createElement('div');
        card.className = 'carousel-item';
        card.innerHTML = `
            <img src="${uploadedImages[index].preview}" alt="${caption.caption}">
            <p>File Name: ${uploadedImages[index].file.name}</p>
            <p>Location: ${caption.metadata.location_info.full_address || 'N/A'}</p>
            <p>Date: ${caption.metadata.labeled_exif['Date/Time'] || 'N/A'}</p>
            <p>Caption: ${caption.caption}</p>
        `;
        captionCarousel.appendChild(card);
        
        // 이미지 데이터를 uploadedImages 배열에 추가
        uploadedImages[index] = {
            ...uploadedImages[index],
            metadata: caption.metadata,
            caption: caption.caption
        };
    });
    captionCarousel.style.display = 'flex';
    writeOptions.style.display = 'block';
    additionalImageUpload.style.display = 'block';
    
    console.log('Updated uploadedImages:', uploadedImages);  // 디버깅용 로그 추가
}

generateContentButton.addEventListener('click', async () => {
    generateContentButton.disabled = true;
    contentSkeleton.style.display = 'block';
    
    try {
        const writingStyle = document.getElementById('writingStyle').value;
        const writingTone = document.getElementById('writingTone').value;
        const writingLength = parseInt(document.getElementById('writingLength').value);
        const creativity = parseFloat(document.querySelector('input[name="creativity"]:checked').value) / 10;
        const userAge = document.getElementById('userAge').value;
        const userGender = document.getElementById('userGender').value;
        
        const result = await generateContent(
            uploadedImages.map(img => ({
                file_name: img.file.name,
                metadata: img.metadata || {},
                caption: img.caption || ''
            })),
            document.getElementById('context').value,
            writingStyle,
            writingTone,
            writingLength,
            creativity,
            {
                age: userAge,
                gender: userGender,
                writing_tone: writingTone
            }
        );
        
        console.log('Sending to server:', {
            imageDataList: uploadedImages.map(img => ({
                file_name: img.file.name,
                metadata: img.metadata || {},
                caption: img.caption || ''
            })),
            userContext: document.getElementById('context').value,
            writingStyle,
            writingTone,
            writingLength,
            temperature: creativity,
            userInfo: {
                age: userAge,
                gender: userGender,
                writing_tone: writingTone
            }
        });  // 디버깅용 로그 추가
content.textContent = result.story;
    hashtags.textContent = result.hashtags;
    generatedContent.style.display = 'block';
    if (isMobile) {
        shareOptions.style.display = 'block';
    }
} catch (error) {
    console.error('글 생성 중 오류 발생:', error);
    alert('글 생성 중 오류가 발생했습니다.');
} finally {
    contentSkeleton.style.display = 'none';
    generateContentButton.disabled = false;
}});
copyContentButton.addEventListener('click', () => {
let textToCopy = '';

// 이미지 정보 추가
uploadedImages.forEach((image, index) => {
    const caption = captionCarousel.children[index];
    textToCopy += `이미지 파일명: ${image.file.name}\n`;
    textToCopy += `촬영 일시: ${caption.children[3].textContent}\n`;
    textToCopy += `촬영 장소: ${caption.children[2].textContent}\n`;
    textToCopy += `캡션: ${caption.children[4].textContent}\n\n`;
});

// 생성된 글과 해시태그 추가
textToCopy += `${content.textContent}\n\n${hashtags.textContent}`;

navigator.clipboard.writeText(textToCopy).then(() => {
    alert('클립보드에 복사되었습니다.');
});});
addMoreImagesButton.addEventListener('click', () => {
fileInput.click();
});
// 여기에 네이버 블로그와 인스타그램 공유 로직 추가
// 예:
// document.getElementById('shareNaverBlog').addEventListener('click', shareToNaverBlog);
// document.getElementById('shareInstagram').addEventListener('click', shareToInstagram);
// function shareToNaverBlog() {
//     // 네이버 블로그 공유 로직
// }
// function shareToInstagram() {
//     // 인스타그램 공유 로직
// }