$(document).ready(function(){
  // Collapse Sidebar Menu
  $('#topnav-hamburger-icon').click(function(){
      var collapseMenu = localStorage.getItem("collapseMenu");
      if (collapseMenu == "YES"){
        localStorage.setItem("collapseMenu","NO");
      }else{
        localStorage.setItem("collapseMenu","YES");
      }
  });
  // Change theme mode (light/dark)
  $('#themeMode').click(function(){
    var themeMode = localStorage.getItem("themeMode");
    if (themeMode == "dark"){
      localStorage.setItem("themeMode","light");
    }else{
      localStorage.setItem("themeMode","dark");
    }
  });
  // Copy Notification count to inner tab
  $('#page-header-notifications-dropdown').click(function(){
    $('#new_notifications').html($('#notification_count').html());
  });
  // Add page title in breadcrumbs
  $('#breadcrumb_pageTitle').html(pageTitleBlock);

  // Datatables Common
  $('.dt-buttons').addClass('btn-group btn-group-sm').attr('role','group');
});



// Supports Moment Date Formats
// Assumption, UTC date is passed as arguements.
function DateConvert(date, $elem = null) {
    var format = 'MMM DD, YY - HH:mm';
    if ($elem && $($elem).attr('data-date-format')) {
        format = $($elem).attr('data-date-format');
    }
    if (!(date.trim().length > 0) || !(moment.utc(date, "YYYY.MM.DD hh:mm a").isValid())) {
        return date;
    }
    return moment(moment.utc(date, "YYYY.MM.DD hh:mm a").toISOString()).format(format);
}

function convertDateToUTC(date) {
    date = new Date(date).toISOString();
    return date;
}

function TimeConvert(date) {
    date = new Date(date);
    var options = {
        year: 'numeric',
        month: '2-digit',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    let newdate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds())).toLocaleString("en-US", options);
    return newdate.split(' ')[1] + ' ' + newdate.split(' ')[2]
}


function DateConvertFullMonth(date) {
    if (date == "") {
        return 'None'
    }
    date = new Date(date);
    var options = {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'};
    let newdate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes())).toLocaleString("en-IN", options)
    return newdate
}

window.onload = function () {
    $('.datecon').each(function () {
        $(this).text(DateConvert($(this).text(), this));
    });
    $('.timecon').each(function () {
        $(this).text(TimeConvert($(this).text()));
    });
    $('.dateconFullMonth').each(function () {
        $(this).text(DateConvertFullMonth($(this).text()));
    });
}

// end_date, start_date must be date objects
function dateDifference(end_date, start_date) {
    if (end_date < start_date) {
        return "Expired"
    }
    var msec = end_date - start_date;
    var mins = Math.floor(msec / 60000);
    var hrs = Math.floor(mins / 60);
    var days = Math.floor(hrs / 24);
    var yrs = Math.floor(days / 365);
    mins = mins % 60;
    hrs = hrs % 24;
    return days + " days, " + hrs + " hours, " + mins + " minutes"
}


window.django = {jQuery: jQuery};