const API_URL = 'https://open.er-api.com/v6/latest/';

const CURRENCIES = [
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CNY', 'CAD',
    'AUD', 'KZT', 'BYN', 'UAH', 'TRY', 'INR', 'PLN'
];

const base1El  = document.getElementById('base1');
const base2El  = document.getElementById('base2');
const targetEl = document.getElementById('target');
const amountEl = document.getElementById('amount');
const button   = document.getElementById('exchange-btn');
const resultEl = document.getElementById('result');

let ratesCache = {};

function fillSelects() {
    [base1El, base2El, targetEl].forEach(select => {
        select.innerHTML = CURRENCIES
            .map(code => `<option value="${code}">${code}</option>`)
            .join('');
    });

    base1El.value  = 'USD';
    base2El.value  = 'EUR';
    targetEl.value = 'RUB';
}

async function getRates(base) {
    if (ratesCache[base]) {
        return ratesCache[base];
    }

    const response = await fetch(API_URL + base);
    if (!response.ok) {
        throw new Error('Ошибка сети: ' + response.status);
    }

    const data = await response.json();
    if (data.result !== 'success' || !data.rates) {
        throw new Error('Некорректный ответ API');
    }

    ratesCache[base] = data.rates;
    return data.rates;
}

async function convert(base, target, amount) {
    const rates = await getRates(base);
    const rate = rates[target];

    if (typeof rate !== 'number') {
        throw new Error(`Курс ${base} → ${target} не найден`);
    }

    return {
        base,
        target,
        rate,
        amount,
        converted: amount * rate
    };
}

async function exchange() {
    const base1  = base1El.value;
    const base2  = base2El.value;
    const target = targetEl.value;
    const amount = parseFloat(amountEl.value) || 0;

    resultEl.innerHTML = '<p class="hint">Загрузка курсов…</p>';
    button.disabled = true;

    try {
        const [first, second] = await Promise.all([
            convert(base1, target, amount),
            convert(base2, target, amount)
        ]);

        render([first, second], amount);
    } catch (error) {
        resultEl.innerHTML =
            `<p class="error">Ошибка: ${error.message}</p>`;
    } finally {
        button.disabled = false;
    }
}

// Вывод результатов в разметку
function render(results, amount) {
    const rows = results.map(item => `
        <div class="row">
            <span>${amount} ${item.base} → ${item.target}</span>
            <span>${item.converted.toFixed(2)}</span>
        </div>
        <div class="row">
            <span>1 ${item.base} → ${item.target}</span>
            <span>${item.rate.toFixed(4)}</span>
        </div>
    `).join('');

    resultEl.innerHTML = rows +
        `<p class="hint">Курсы на ${new Date().toLocaleString('ru-RU')}</p>`;
}

fillSelects();
button.addEventListener('click', exchange);