var delay = document.getElementById('delay');
var delay_display = document.getElementById('delay_display');
// delay_display.innerHTML = delay.value + 's';

try {
    delay.oninput = function() {
        delay_display.innerHTML = delay.value + 's';
    }
} catch (error) {
    
}

function showBlackListSettings() {
    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';
}
function hideBlackListSettings() {
    document.getElementById('blacklist-list').style.display = '';
    document.getElementById('blacklist-settings').style.display = '';
}
function confirmBlackListSettings() {
    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';

    //add blacklist to table

    hideBlackListSettings();
}

function start() {
    $('#startstop').html('<div class="loading"></div>')

    setTimeout(function() {
        $('#startstop').html('Stop')
        $('#startstop').attr('onclick', 'stop();')

    }, 3000);
}

function stop() {
    $('#startstop').html('<div class="loading"></div>')

    setTimeout(function() {
        $('#startstop').html('Start')
        $('#startstop').attr('onclick', 'start();')
    }, 3000);
}

function showInfo(title, text) {
    $('#title').html(title)
    $('#info-hidden').html('<p style="line-height:30px;">' + text + '</p>')
    $('#table-buttons').css({display: 'none'})
    $('#info-hidden, #back').css({display: 'block'})
}

function closeInfo() {
    $('#title').html('FAQ')
    $('#table-buttons').css({display: 'block'})
    $('#info-hidden, #back').css({display: 'none'})
}