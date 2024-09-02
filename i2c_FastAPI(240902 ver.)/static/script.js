document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    // API 기본 URL 설정
    const API_BASE_URL = '';

    // DOM 요소 선택
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const generateCaptionsButton = document.getElementById('generateCaptions');
    const captionCarousel = document.getElementById('captionCarousel');
    const writeOptions = document.getElementById('writeOptions');
    const generateContentButton = document.getElementById('generateContent');
    const generatedContent = document.getElementById('generatedContent');
    const contentSkeleton = document.getElementById('contentSkeleton');
    const content = document.getElementById('content');
    const hashtags = document.getElementById('hashtags');
    const copyContentButton = document.getElementById('copyContent');
    const userAgeSelect = document.getElementById('age');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const themeToggle = document.getElementById('theme-toggle');

    // 전역 변수
    let uploadedImages = [];
    let currentCarouselPosition = 0;

    // 사이드바 토글 기능
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });

    // 나이 선택 옵션 생성
    for (let i = 99; i >= 0; i--) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        userAgeSelect.appendChild(option);
    }

    // 드래그 앤 드롭 이벤트 리스너
    dropzone.addEventListener('click', () => fileInput.click());
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

    // 파일 처리 함수
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

    // 이미지 프리뷰 추가 함수
    function addImagePreview(file, preview) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'imagePreview';

        const img = document.createElement('img');
        img.src = preview;
        img.style.width = '50px';
        img.style.height = '50px';
        img.style.objectFit = 'cover';

        const removeButton = document.createElement('button');
        removeButton.textContent = 'X';
        removeButton.className = 'removeImage';
        removeButton.addEventListener('click', () => removeImage(imageContainer, file));

        imageContainer.appendChild(img);
        imageContainer.appendChild(removeButton);
        dropzone.appendChild(imageContainer);

        uploadedImages.push({
            file: file,
            preview: preview,
            container: imageContainer
        });
    }

    // 이미지 제거 함수
    function removeImage(container, file) {
        container.remove();
        uploadedImages = uploadedImages.filter(img => img.file !== file);
        if (uploadedImages.length === 0) {
            generateCaptionsButton.style.display = 'none';
        }
    }

    // 글쓰기 스타일과 톤 로딩 함수
    async function loadWritingStylesAndTones() {
        try {
            const stylesResponse = await fetch(`${API_BASE_URL}/writing-styles/`);
            const tonesResponse = await fetch(`${API_BASE_URL}/writing-tones/`);
            const stylesData = await stylesResponse.json();
            const tonesData = await tonesResponse.json();

            const writingStyleContainer = document.getElementById('writingStyle');
            const writingToneContainer = document.getElementById('writingTone');

            writingStyleContainer.innerHTML = '';
            stylesData.styles.forEach((style, index) => {
                const radioButton = document.createElement('input');
                radioButton.type = 'radio';
                radioButton.id = `style${index + 1}`;
                radioButton.name = 'writingStyle';
                radioButton.value = style;

                const label = document.createElement('label');
                label.htmlFor = `style${index + 1}`;
                label.textContent = style;
                label.title = `${style} 스타일로 글을 작성합니다.`;

                writingStyleContainer.appendChild(radioButton);
                writingStyleContainer.appendChild(label);
            });

            writingToneContainer.innerHTML = '';
            Object.entries(tonesData.tones).forEach(([key, value]) => {
                const radioButton = document.createElement('input');
                radioButton.type = 'radio';
                radioButton.id = `tone${key}`;
                radioButton.name = 'writingTone';
                radioButton.value = key;

                const label = document.createElement('label');
                label.htmlFor = `tone${key}`;
                label.textContent = value[0]; // 두 번째 값 (예: 'formal')
                label.title = value[1]; // 첫 번째 값 (예: '존댓말 스타일')

                writingToneContainer.appendChild(radioButton);
                writingToneContainer.appendChild(label);
            });
        } catch (error) {
            console.error('글쓰기 스타일과 톤을 불러오는 중 오류 발생:', error);
        }
    }

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

    // 캡션 생성 버튼 이벤트 리스너
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

    // 캡션 표시 함수
    function displayCaptions(captions) {
        captionCarousel.innerHTML = '';
        captions.forEach((caption, index) => {
            const card = document.createElement('div');
            card.className = 'carousel-item';
            const dateStr = caption.metadata.labeled_exif['Date/Time'];
            let formattedDate = '날짜 정보 없음';
            if (dateStr) {
                const date = new Date(dateStr.replace(/(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})/, '$1-$2-$3T$4:$5:$6'));
                if (!isNaN(date.getTime())) {
                    formattedDate = `${date.getFullYear()}년 ${String(date.getMonth() + 1).padStart(2, '0')}월 ${String(date.getDate()).padStart(2, '0')}일 ${String(date.getHours()).padStart(2, '0')}시 ${String(date.getMinutes()).padStart(2, '0')}분`;
                }
            }
            card.innerHTML = `
                <img src="${uploadedImages[index].preview}" alt="${caption.caption}">
                <div class="metadata">
                    <p>날짜: ${formattedDate}</p>
                    <p>주소: ${caption.metadata.location_info.full_address || 'N/A'}</p>
                    <p>이미지 캡션: ${caption.caption}</p>
                </div>
            `;
            captionCarousel.appendChild(card);

            uploadedImages[index] = {
                ...uploadedImages[index],
                metadata: caption.metadata,
                caption: caption.caption
            };
        });
        document.getElementById('captionResults').style.display = 'block';
        writeOptions.style.display = 'block';
        updateCarouselButtons();
    }

    // 캐러셀 위치 업데이트 함수
    function updateCarouselPosition() {
        captionCarousel.style.transform = `translateX(-${currentCarouselPosition}px)`;
    }

    // 캐러셀 버튼 상태 업데이트 함수
    function updateCarouselButtons() {
        const carouselWidth = captionCarousel.offsetWidth;
        const maxPosition = captionCarousel.scrollWidth - carouselWidth;

        prevButton.disabled = currentCarouselPosition <= 0;
        nextButton.disabled = currentCarouselPosition >= maxPosition;
    }

    // 이전 버튼 이벤트 리스너
    prevButton.addEventListener('click', () => {
        const itemWidth = document.querySelector('.carousel-item').offsetWidth;
        currentCarouselPosition = Math.max(currentCarouselPosition - itemWidth, 0);
        updateCarouselPosition();
        updateCarouselButtons();
    });

    // 다음 버튼 이벤트 리스너
    nextButton.addEventListener('click', () => {
        const itemWidth = document.querySelector('.carousel-item').offsetWidth;
        const carouselWidth = captionCarousel.offsetWidth;
        const maxPosition = captionCarousel.scrollWidth - carouselWidth;
        currentCarouselPosition = Math.min(currentCarouselPosition + itemWidth, maxPosition);
        updateCarouselPosition();
        updateCarouselButtons();
    });

    // 글 생성 버튼 이벤트 리스너
    generateContentButton.addEventListener('click', async () => {
        generateContentButton.disabled = true;
        contentSkeleton.style.display = 'block';

        try {
            const writingStyle = document.querySelector('input[name="writingStyle"]:checked').value;
            const writingTone = document.querySelector('input[name="writingTone"]:checked').value;
            const writingLength = document.getElementById('length').value;
            const creativity = document.querySelector('input[name="creativity"]:checked').value;
            const userAge = document.getElementById('age').value;
            const userGender = document.getElementById('gender').value;

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

            content.textContent = result.story;
            hashtags.textContent = result.hashtags;
            generatedContent.style.display = 'block';
        } catch (error) {
            console.error('글 생성 중 오류 발생:', error);
            alert('글 생성 중 오류가 발생했습니다.');
        } finally {
            contentSkeleton.style.display = 'none';
            generateContentButton.disabled = false;
        }
    });

    // 클립보드 복사 버튼 이벤트 리스너
    copyContentButton.addEventListener('click', () => {
        let textToCopy = '';

        const captionItems = document.querySelectorAll('.carousel-item');
        captionItems.forEach((item) => {
            const metadata = item.querySelector('.metadata');
            textToCopy += metadata.textContent + '\n\n';
        });

        textToCopy += `${content.textContent}\n\n${hashtags.textContent}`;

        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('클립보드에 복사되었습니다.');
        }).catch(err => {
            console.error('클립보드 복사 중 오류 발생:', err);
            alert('클립보드 복사에 실패했습니다.');
        });
    });

// 다크모드 토글 이벤트 리스너
themeToggle.addEventListener('change', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

// 페이지 로드 시 다크모드 상태 복원
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    themeToggle.checked = true;
}

// 모바일 환경에서 터치 이벤트 처리
if ('ontouchstart' in window) {
    document.body.addEventListener('touchstart', function() {}, false);
}

// 모바일에서 캐러셀 스와이프 기능 추가
let touchstartX = 0;
let touchendX = 0;

captionCarousel.addEventListener('touchstart', e => {
    touchstartX = e.changedTouches[0].screenX;
});

captionCarousel.addEventListener('touchend', e => {
    touchendX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (touchendX < touchstartX) nextButton.click();
    if (touchendX > touchstartX) prevButton.click();
}

// 모바일에서 이미지 업로드 시 파일 선택 다이얼로그 열기
if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
}

// 페이지 로드 시 실행할 함수들
function initializePage() {
    loadWritingStylesAndTones();
    // 기타 초기화 코드...
}

// 페이지 로드 시 초기화 함수 실행
initializePage();
});

// 전역 스코프에서 실행되는 코드
console.log('Script loaded');