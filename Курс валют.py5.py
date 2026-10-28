<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Конвертер валют — две базовые валюты</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="app">
        <h1>Конвертер валют</h1>

        <div class="field">
            <label for="base1">Базовая валюта 1</label>
            <select id="base1"></select>
        </div>

        <div class="field">
            <label for="base2">Базовая валюта 2</label>
            <select id="base2"></select>
        </div>

        <div class="field">
            <label for="target">Целевая валюта</label>
            <select id="target"></select>
        </div>

        <div class="field">
            <label for="amount">Сумма</label>
            <input id="amount" type="number" min="0" value="1">
        </div>

        <button id="exchange-btn">Конвертировать</button>

        <div id="result" class="result"></div>
    </div>

    <script src="js/script.js"></script>
</body>
</html>