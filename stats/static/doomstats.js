function on_date_modified(dateText, inst) {
	if ($(this).attr('id') == 'date-day') {
		var date = $(this).val();
		goto_date(date, date);
	} else {
		reload_dates();
	}
}

function reload_dates() {
	var datefrom = $('#date-from').val();
	var dateto = $('#date-to').val();
	goto_date(datefrom, dateto)
}

function goto_date(datefrom, dateto) {
	var current = URI.parseQuery(location.search);
	if (current["datefrom"] != datefrom || current["dateto"] != dateto) {
		var uri = new URI();
		uri.setQuery("datefrom", datefrom);
		uri.setQuery("dateto", dateto);
		location.href = uri.href();
	}
}

function apply_dateranges_to_a_hrefs() {
	var mainQuery = URI.parseQuery(new URI().query());
	$('a').each(function() {
		var uri = $(this).uri()
		if (!uri.scheme() && !$(this).hasClass('no-daterange')) {
			uri.setQuery("datefrom", mainQuery["datefrom"]);
			uri.setQuery("dateto", mainQuery["dateto"]);
		}
	});
}

$(document).ready(function() {
	$('.datepicker').datepicker({
		dateFormat: "yy-mm-dd",
		onSelect: on_date_modified
	});

	$('.no-javascript').hide();

	apply_dateranges_to_a_hrefs();
	if ($('#date-from').length && $('#date-to').length) {
		$('#date-from').val(sitedata["date-from"])
		$('#date-to').val(sitedata["date-to"])
		reload_dates();
	}
});
