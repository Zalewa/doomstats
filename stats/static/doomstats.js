function reload_dates() {
	var datefrom = $('#date-from').datepicker("getDate");
	var dateto = $('#date-to').datepicker("getDate");
	var timefrom = date_to_stamp(datefrom);
	var timeto = date_to_stamp(dateto);
	var newSearch = '?datefrom=' + timefrom + '&dateto=' + timeto;
	if (newSearch != location.search) {
		location.search = newSearch;
	}
}

function date_to_stamp(date) {
	return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate()
}

$(document).ready(function() {
	$('.datepicker').datepicker({
		dateFormat: "yy-mm-dd",
		onSelect: function(dateText, inst) {
			reload_dates()
		}
	});

	if ($('#date-from').length && $('#date-to').length) {
		$('#date-from').datepicker("setDate", new Date(sitedata["date-from"] * 1000.0));
		$('#date-to').datepicker("setDate", new Date(sitedata["date-to"] * 1000.0));
		reload_dates();
	}
});
