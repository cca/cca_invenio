// link to API representation of current page
const html = `<div class="item"><a href="/api${location.pathname}?${location.search}">API</a></div>`
$('#invenio-menu > .item').not('.right').last().after(html)
