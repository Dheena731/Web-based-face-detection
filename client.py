<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Face Recognition</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 1rem;
      background-color: #f5f7fa;
    }
    #dropZone {
      border: 3px dashed #888;
      border-radius: 10px;
      padding: 2rem;
      width: 90%;
      max-width: 600px;
      text-align: center;
      background: #fff;
      margin-bottom: 1rem;
      transition: background 0.3s;
    }
    #dropZone.dragover {
      background: #e0f0ff;
    }
    canvas {
      border: 2px solid #ccc;
      border-radius: 8px;
      max-width: 100%;
    }
    #results {
      margin-top: 1rem;
      background: #fff;
      padding: 1rem;
      border-radius: 10px;
      width: 100%;
      max-width: 600px;
    }
    #spinner {
      display: none;
    }
    button {
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      font-size: 1rem;
      cursor: pointer;
      border: none;
      border-radius: 8px;
      background-color: #007bff;
      color: white;
    }
  </style>
</head>
<body>
  <h1>Face Recognition</h1>

  <div id="dropZone">Drag and drop an image here or click to upload</div>
  <input type="file" id="fileInput" style="display:none;" accept="image/*" />
  <button id="webcamBtn">📸 Use Webcam</button>

  <video id="video" autoplay playsinline style="display:none; margin-top:1rem; border-radius:10px;"></video>
  <canvas id="webcamCanvas" style="display:none;"></canvas>
  <button id="snapBtn" style="display:none;">📷 Capture</button>

  <div id="spinner">🔄 Detecting faces...</div>
  <canvas id="canvas" width="400"></canvas>
  <div id="results"></div>

  <script>
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const resultDiv = document.getElementById("results");
    const spinner = document.getElementById("spinner");
    const webcamBtn = document.getElementById("webcamBtn");
    const video = document.getElementById("video");
    const webcamCanvas = document.getElementById("webcamCanvas");
    const snapBtn = document.getElementById("snapBtn");
    const MAX_WIDTH = 600;

    dropZone.addEventListener("click", () => fileInput.click());
    dropZone.addEventListener("dragover", e => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", e => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener("change", e => handleFile(e.target.files[0]));

    function showSpinner(show) {
      spinner.style.display = show ? "block" : "none";
    }

    async function handleFile(file) {
      const img = new Image();
      const reader = new FileReader();
      reader.onload = e => {
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);

      img.onload = async () => {
        const scale = Math.min(MAX_WIDTH / img.width, 1);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
        const formData = new FormData();
        formData.append("image", blob, "upload.jpg");

        showSpinner(true);
        const response = await fetch("/recognize_face", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        showSpinner(false);

        ctx.strokeStyle = "red";
        ctx.lineWidth = 2;
        ctx.font = "16px 'Segoe UI'";
        ctx.fillStyle = "red";

        resultDiv.innerHTML = data.results.length
          ? "<h2>Detected Faces:</h2><ul>"
          : "<p style='color:gray;'>No faces detected.</p>";

        for (const face of data.results) {
          const [x, y, w, h] = face.box;
          ctx.strokeRect(x, y, w, h);
          ctx.fillText(face.name, x + 2, y - 8);
          resultDiv.innerHTML += `<li><strong>${face.name}</strong> at (x:${x}, y:${y})</li>`;
        }

        if (data.results.length) resultDiv.innerHTML += "</ul>";
      };
    }

    webcamBtn.addEventListener("click", async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = "block";
        snapBtn.style.display = "inline-block";
      } catch (err) {
        alert("Webcam access denied or unavailable.");
      }
    });

    snapBtn.addEventListener("click", async () => {
      const width = video.videoWidth;
      const height = video.videoHeight;
      webcamCanvas.width = width;
      webcamCanvas.height = height;
      const webcamCtx = webcamCanvas.getContext("2d");
      webcamCtx.drawImage(video, 0, 0, width, height);

      const tracks = video.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      video.style.display = "none";
      snapBtn.style.display = "none";

      const scale = Math.min(MAX_WIDTH / width, 1);
      canvas.width = width * scale;
      canvas.height = height * scale;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(webcamCanvas, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
      const formData = new FormData();
      formData.append("image", blob, "webcam.jpg");

      showSpinner(true);
      const response = await fetch("/recognize_face", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      showSpinner(false);

      ctx.strokeStyle = "red";
      ctx.lineWidth = 2;
      ctx.font = "16px 'Segoe UI'";
      ctx.fillStyle = "red";

      resultDiv.innerHTML = data.results.length
        ? "<h2>Detected Faces:</h2><ul>"
        : "<p style='color:gray;'>No faces detected.</p>";

      for (const face of data.results) {
        const [x, y, w, h] = face.box;
        ctx.strokeRect(x, y, w, h);
        ctx.fillText(face.name, x + 2, y - 8);
        resultDiv.innerHTML += `<li><strong>${face.name}</strong> at (x:${x}, y:${y})</li>`;
      }

      if (data.results.length) resultDiv.innerHTML += "</ul>";
    });
  </script>
</body>
</html>
