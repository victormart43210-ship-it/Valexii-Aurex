const cards = document.getElementById('cards');
const overall = document.getElementById('overall');
async function refresh() {
  overall.textContent = 'CHECKING…';
  cards.replaceChildren();
  try {
    const res = await fetch('/api/status', {cache: 'no-store', credentials: 'same-origin'});
    if (!res.ok) throw new Error('Local probe unavailable');
    const payload = await res.json();
    overall.textContent = 'LOCAL RESULT: ' + payload.overall + ' · INDEPENDENT VERIFICATION: NOT VERIFIED';
    for (const item of payload.checks) {
      const card = document.createElement('article');
      const title = document.createElement('h3');
      const summary = document.createElement('p');
      title.textContent = 'GET /v1/' + item.endpoint;
      summary.textContent = item.status + (item.reason ? ' · ' + item.reason : '') +
        (typeof item.count === 'number' ? ' · ' + item.count + ' records' : '') +
        (item.zeroDollarBudget === true ? ' · $0 limit' : '');
      card.append(title, summary);
      cards.append(card);
    }
  } catch {
    overall.textContent = 'HOLD — LOCAL BACKEND UNAVAILABLE';
  }
}
document.getElementById('refresh').addEventListener('click', refresh);
refresh();
