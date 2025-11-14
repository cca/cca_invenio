// link to API representation of current page
const apiUrl = "/api" + location.pathname + location.search
const $apiDiv = $('<div class="item"><a></a></div>')
$apiDiv.find('a').attr('href', apiUrl).text('API')
$('#invenio-menu > .item').not('.right').last().after($apiDiv)
