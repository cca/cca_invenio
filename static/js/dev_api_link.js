// link to API representation of current page
const qs = location.search ? "?" + location.search : ""
const html = `<div class="item"><a href="/api${location.pathname}${qs}">API</a></div>`
$('#invenio-menu > .item').not('.right').last().after(html)
