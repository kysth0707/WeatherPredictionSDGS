document.firstElementChild.style.zoom = window.innerHeight/939;

window.addEventListener("resize", function() {
	document.firstElementChild.style.zoom = window.innerHeight/939;
})

document.getElementById('file').addEventListener('change', function(event) {
	const fileInput = event.target;
	const file = fileInput.files[0]; // 선택한 파일을 가져옵니다.

	if (!file) {
		alert('파일이 선택되지 않았습니다');
		return;
	}

	const checkServerStatus = () => {
		return fetch('http://nojam.easylab.kr:456/api/ok')
			.then(response => response.json())
	};

	const reader = new FileReader();
	reader.onload = function(e) {
		document.body.style.backgroundImage = `url(${e.target.result})`;
	};
	reader.readAsDataURL(file);

	const uploadFile = () => {
		const formData = new FormData();
		formData.append('file', file);

		fetch('http://nojam.easylab.kr:456/api/predict', {
			method: 'POST',
			body: formData
		})
		.then(response => response.json())
		.then(data => {
			if (data.Status !== true) {
				document.getElementById("uploadtext").textContent = "너무 빠른 요청";
				setTimeout(() => {
					document.getElementById("uploadtext").textContent = "이미지 예측하기";
				}, 2000);
				return;
			}

			const percent1 = parseFloat(data.prediction.cloud) * 100;
			const percent2 = parseFloat(data.prediction.rain) * 100;
			document.getElementById("cloudtext").textContent = percent1.toFixed() + '%';
			document.getElementById("raintext").textContent = percent2.toFixed() + '%';

			document.getElementById("uploadtext").textContent = "예측 완료!";
			setTimeout(() => {
				document.getElementById("uploadtext").textContent = "이미지 예측하기";
			}, 2000);
		})
		.catch(error => {
			console.error(error);
			alert("처리 중 오류가 발생했습니다.\nError at console");
		});
	};

	checkServerStatus()
		.then(isServerOk => {
			if (isServerOk) {
				uploadFile();
			} else {
				document.getElementById("uploadtext").textContent = "서버 연결 불안정";
				alert("서버 연결이 불안정합니다");
				setTimeout(() => {
					document.getElementById("uploadtext").textContent = "이미지 예측하기";
				}, 2000);
			}
		})
		.catch(error => {
			console.error('Error:', error);
			document.getElementById("uploadtext").textContent = "서버 연결 불안정";
			alert("서버 연결이 불안정합니다");
			setTimeout(() => {
				document.getElementById("uploadtext").textContent = "이미지 예측하기";
			}, 2000);
		});
});
