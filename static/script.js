// ================= THEME TOGGLE =================
const themeToggle = document.getElementById("themeToggle");
if (themeToggle) {
  const stored = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-bs-theme", stored);
  themeToggle.checked = stored === "dark";
  themeToggle.addEventListener("change", () => {
    const theme = themeToggle.checked ? "dark" : "light";
    document.documentElement.setAttribute("data-bs-theme", theme);
    localStorage.setItem("theme", theme);
  });
}

// ================= SHOW TOAST =================
const showToast = (message, bg = "danger") => {
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-bg-${bg} border-0 show`;
  toast.role = "alert";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  document.querySelector(".toast-container").appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
};

// ================= LOGIN HANDLER =================
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username");
    const password = document.getElementById("password");

    const res = await fetch("http://localhost:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",  // ✅ Must be included
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    });
    

    const data = await res.json();
    if (data.success) {
      window.location.href = "/";  // ✅ Correct redirect
    } else {
      showToast(data.message || "Login failed");
    }
  });
}

// ================= LOGOUT HANDLER =================
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    await fetch("http://localhost:5000/logout", {
      method: "POST",
      credentials: "include"
    });
    window.location.href = "login.html";
  });
}

// ================= SESSION CHECK =================
window.addEventListener("DOMContentLoaded", async () => {
  if (!document.getElementById("csvForm")) return;
  try {
    const res = await fetch("http://localhost:5000/check_session", {
      method: "GET",
      credentials: "include"
    });
    const data = await res.json();
    if (!data.logged_in) {
      window.location.href = "login.html";
    }
  } catch (err) {
    console.error(err);
  }
});

// ================= FORM SUBMIT =================
const form = document.getElementById("csvForm");
if (form) {
  let chartInstance = null;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    document.getElementById("loader").style.display = "block";

    const file = document.getElementById("csvFile").files[0];
    const target = document.getElementById("target").value;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await fetch("/upload_csv", {
        method: "POST",
        credentials: "include",
        body: formData
      });
      const uploadData = await uploadRes.json();
      if (uploadData.error) return showToast(uploadData.error);

      const table = document.getElementById("previewTable");
      table.innerHTML = "";
      const preview = uploadData.preview;
      if (preview && preview.length > 0) {
        const headers = Object.keys(preview[0]);
        const thead = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead>`;
        const tbody = preview.map(row =>
          `<tr>${headers.map(h => `<td>${row[h]}</td>`).join("")}</tr>`).join("");
        table.innerHTML = thead + "<tbody>" + tbody + "</tbody>";
      }

      const predictRes = await fetch("/predict", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target })
      });
      const result = await predictRes.json();
      if (result.error) return showToast(result.error);

      const predictions = result.predictions;
      const actual = result.actual;

      const ctx = document.getElementById("predictionChart").getContext("2d");
      if (chartInstance) chartInstance.destroy();
      chartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: predictions.map((_, i) => `T+${i+1}`),
          datasets: [
            { label: "Predicted", data: predictions, borderColor: "#0d6efd", tension: 0.4 },
            { label: "Actual", data: actual, borderColor: "#198754", tension: 0.4 }
          ]
        }
      });

      document.getElementById("values").innerHTML = `
        <h5>Predicted:</h5><p>${predictions.join(", ")}</p>
        ${actual.length ? `<h5>Actual:</h5><p>${actual.join(", ")}</p>` : ""}
      `;

      await fetch("/explain", { credentials: "include" });
      document.getElementById("shapImage").src = "static/shap_plot.png";
      document.getElementById("shapImage").style.display = "block";
    } catch (err) {
      console.error(err);
      showToast("Something went wrong");
    } finally {
      document.getElementById("loader").style.display = "none";
    }
  });

  document.getElementById("downloadBtn").onclick = () => {
    window.location.href = "/download_predictions";
  };
}
