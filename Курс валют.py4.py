* { box-sizing: border-box; }

body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f4f5f7;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: #1c1e21;
}

.app {
    width: 100%;
    max-width: 460px;
    padding: 28px 32px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, .08);
}

h1 {
    margin: 0 0 20px;
    font-size: 22px;
    font-weight: 600;
}

.field {
    margin-bottom: 14px;
}

label {
    display: block;
    margin-bottom: 6px;
    font-size: 13px;
    color: #606770;
}

select,
input {
    width: 100%;
    padding: 10px 12px;
    font-size: 15px;
    border: 1px solid #d0d3d8;
    border-radius: 8px;
    background: #fff;
}

select:focus,
input:focus {
    outline: none;
    border-color: #2f6fed;
}

button {
    width: 100%;
    margin-top: 6px;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    background: #2f6fed;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background .15s;
}

button:hover { background: #1f5bd8; }
button:disabled { background: #9db4e6; cursor: default; }

.result {
    margin-top: 18px;
    font-size: 15px;
    line-height: 1.55;
}

.result .row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0;
    border-top: 1px solid #eceef1;
}

.result .row span:last-child {
    font-weight: 600;
}

.error { color: #d93025; }
.hint  { color: #8a8f98; font-size: 14px; }
