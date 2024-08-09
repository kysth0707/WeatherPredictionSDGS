const waitForEnd = 500;
document.firstElementChild.style.zoom = window.innerHeight/939;

window.addEventListener("resize", function() {
	document.firstElementChild.style.zoom = window.innerHeight/939;
})

document.getElementById('file').addEventListener('change', function(event) {
	const fileInput = event.target;
	const file = fileInput.files[0];

	if (!file) {
		alert('파일이 선택되지 않았습니다');
		return;
	}

	const checkServerStatus = () => {
		return fetch('http://nojam.easylab.kr:456/api/ok')
			.then(response => response.json());
	};

	const reader = new FileReader();
	reader.onload = function(e) {
		document.body.style.backgroundImage = `url(${e.target.result})`;
	};
	reader.readAsDataURL(file);

	const uploadFile = () => {
		const formData = new FormData();
		formData.append('file', file);

		const xhr = new XMLHttpRequest();
		xhr.open('POST', 'http://nojam.easylab.kr:456/api/predict', true);

		// 업로드 시작 시
		document.getElementById('upload-label').style.display = 'none';  // 버튼 숨기기
		const progressContainer = document.getElementById('progress-container');
		const progressText = document.getElementById('progress-text');
		progressContainer.style.display = 'block';  // 프로그래스 바 표시
		setTimeout(() => {
			progressContainer.classList.add('expand');  // 프로그래스 바 확장
		}, 10);

		xhr.upload.addEventListener('progress', function(e) {
			if (e.lengthComputable) {
				const percentComplete = (e.loaded / e.total) * 100;
				document.getElementById('progress-bar').style.width = percentComplete + '%';
				progressText.textContent = Math.round(percentComplete) + '%';  // 진행률 업데이트
			}
		});

		xhr.addEventListener('load', function() {
			document.getElementById('progress-bar').style.width = '100%';
			progressText.textContent = '100%';
			const response = JSON.parse(xhr.responseText);
			if (response.Status !== true) {
				document.getElementById("uploadtext").textContent = "너무 빠른 요청";
				setTimeout(() => {
					progressContainer.classList.remove('expand');  // 프로그래스 바 축소
					setTimeout(() => {
						document.getElementById('progress-bar').style.width = '0%';
						progressText.textContent = '0%';
						progressContainer.style.display = 'none';  // 프로그래스 바 숨기기
						document.getElementById('upload-label').style.display = 'block';  // 버튼 표시
						document.getElementById("uploadtext").textContent = "이미지 예측하기";
					}, 500);  // 축소 애니메이션 시간이 끝난 후에 display를 변경
				}, waitForEnd);
				return;
			}

			const percent1 = parseFloat(response.prediction.cloud) * 100;
			const percent2 = parseFloat(response.prediction.rain) * 100;
			document.getElementById("cloudtext").textContent = percent1.toFixed() + '%';
			document.getElementById("raintext").textContent = percent2.toFixed() + '%';

			setTimeout(() => {
				progressContainer.classList.remove('expand');  // 프로그래스 바 축소
				setTimeout(() => {
					document.getElementById('progress-bar').style.width = '0%';
					progressText.textContent = '0%';
					progressContainer.style.display = 'none';  // 프로그래스 바 숨기기
					document.getElementById('upload-label').style.display = 'block';  // 버튼 표시
					document.getElementById("uploadtext").textContent = "이미지 예측하기";
				}, 500);  // 축소 애니메이션 시간이 끝난 후에 display를 변경
			}, waitForEnd);
		});

		xhr.addEventListener('error', function() {
			console.error('Error:', xhr.statusText);
			alert("처리 중 오류가 발생했습니다.\nError at console");
			progressContainer.classList.remove('expand');  // 프로그래스 바 축소
			setTimeout(() => {
				document.getElementById('progress-bar').style.width = '0%';
				progressText.textContent = '0%';
				progressContainer.style.display = 'none';  // 프로그래스 바 숨기기
				document.getElementById('upload-label').style.display = 'block';  // 버튼 표시
			}, 500);  // 축소 애니메이션 시간이 끝난 후에 display를 변경
		});

		xhr.send(formData);
	};

	checkServerStatus()
		.then(isServerOk => {
			if (isServerOk) {
				document.getElementById('progress-bar').style.width = '0%'; // 프로그래스 바 초기화
				document.getElementById('progress-text').textContent = '0%'; // 텍스트 초기화
				uploadFile();
			} else {
				document.getElementById("uploadtext").textContent = "서버 연결 불안정";
				alert("서버 연결이 불안정합니다");
				setTimeout(() => {
					document.getElementById("uploadtext").textContent = "이미지 예측하기";
				}, waitForEnd);
			}
		})
		.catch(error => {
			console.error('Error:', error);
			document.getElementById("uploadtext").textContent = "서버 연결 불안정";
			alert("서버 연결이 불안정합니다");
			setTimeout(() => {
				document.getElementById("uploadtext").textContent = "이미지 예측하기";
			}, waitForEnd);
		});
});
