function on_date_modified(dateText, inst) {
	if ($(this).attr('id') == 'date-day') {
		var date = $(this).datepicker('getDate');
		goto_date(date, date);
	} else {
		reload_dates();
	}
}

function reload_dates() {
	var datefrom = $('#date-from').datepicker("getDate");
	var dateto = $('#date-to').datepicker("getDate");
	goto_date(datefrom, dateto)
}

function goto_date(datefrom, dateto) {
	var timefrom = date_to_stamp(datefrom);
	var timeto = date_to_stamp(dateto);
	var current = URI.parseQuery(location.search);
	if (current["datefrom"] != timefrom || current["dateto"] != timeto) {
		var uri = new URI();
		uri.setQuery("datefrom", timefrom);
		uri.setQuery("dateto", timeto);
		location.href = uri.href();
	}
}


function date_to_stamp(date) {
	return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate()
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
		$('#date-from').datepicker("setDate", new Date(sitedata["date-from"] * 1000.0));
		$('#date-to').datepicker("setDate", new Date(sitedata["date-to"] * 1000.0));
		reload_dates();
	}
});
