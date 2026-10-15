'use strict';
let token = '';
let cursor = null;
const el = id => document.getElementById(id);
const status = text => { el('state').textContent = text; };
const clean = () => { el('jobs').replaceChildren(); el('more').hidden = true; cursor = null; };
async function load(reset) {
  if (reset) { token = el('token').value; el('token').value = ''; clean(); }
  if (!token) { status('Token required'); return; }
  status('Loading…');
  const query = new URLSearchParams({limit:'20'});
  if (cursor) query.set('cursor', cursor);
  try {
    const response = await fetch('/v1/jobs?' + query, {headers: {Authorization: 'Bearer ' + token}, cache: 'no-store'});
    if (!response.ok) { status('Request failed: HTTP ' + response.status); return; }
    const data = await response.json();
    for (const job of data.jobs) {
      const tr = document.createElement('tr');
      for (const value of [job.id, job.kind, job.state, new Date(job.createdAt * 1000).toLocaleString()]) {
        const td = document.createElement('td'); td.textContent = String(value); tr.append(td);
      }
      el('jobs').append(tr);
    }
    cursor = data.nextCursor;
    el('more').hidden = !cursor;
    status('Read-only · ' + el('jobs').children.length + ' shown');
  } catch (_) { status('Connection unavailable'); }
}
el('load').addEventListener('click', () => load(true));
el('more').addEventListener('click', () => load(false));
el('clear').addEventListener('click', () => {token=''; el('token').value=''; clean(); status('Cleared');});
