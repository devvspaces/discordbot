// Codes for ajax setup for get and post requests to backend
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


let csrftoken = getCookie('csrftoken');


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}



try{
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
} catch(e){
	console.log(e)
}


// js
var delay = document.getElementById('delay');
var delay_display = document.getElementById('delay_display');
// delay_display.innerHTML = delay.value + 's';

delay.oninput = function() {
    delay_display.innerHTML = delay.value + 's';
}

function showBlackListSettings() {
    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';
}
function hideBlackListSettings() {
    document.getElementById('blacklist-list').style.display = '';
    document.getElementById('blacklist-settings').style.display = '';
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


// Codes for popup messages
let popup = $('.popup')
function togglePopup(message){
    popup.addClass('active')
    popup[0].lastElementChild.innerText = message
    setTimeout(() => {
        popup.removeClass('active')
    }, 5000);
}

let connect_server_btns = document.querySelectorAll('.connect_server')
let remove_server_btns = document.querySelectorAll('.remove_server')

// Clicking connect_server_btn and remove server event ajax
function clickServerConnect(e) {
    // GEt the connect uid
    e.preventDefault()
    connect_id = e.target.parentElement.getAttribute('connect_id')

    // Know which kind of request to make (connect/remove)
    let req_type = 'connect'
    if (e.target.classList.contains('remove_server')){
        req_type = 'remove'

        // Confirm user wants to remove server
        let confimation = confirm("Are you sure to remove this server?")

        if (confimation == false){
            return
        }
    }  

    // Create a string in serializable format and send with ajax
    let serverLink = 'connect_id='+connect_id+'&req_type='+req_type

    let thisURL = window.location.href // or set your own url

    loadStart('#serverAdding')

    $.ajax({
        method: "POST",
        url: thisURL,
        data: serverLink,
        success: function (data){
            loadStop('#serverAdding')

            if (req_type=='remove'){
                e.target.parentElement.parentElement.remove()
            }
            
            // Get message display on popup
            message = data['message']
            togglePopup(message)
        },
        error: function (jqXHR) {
            loadStop('#serverAdding')

            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message)
        },
    })
}

// Code for connect_server
function listenToConnectBtns() {
    connect_server_btns = document.querySelectorAll('.connect_server')
    connect_server_btns.forEach(i=>{
        i.addEventListener('click', clickServerConnect)
    })
}

listenToConnectBtns()

// Code for remove_server
function listenToRemoveBtns() {
    remove_server_btns = document.querySelectorAll('.remove_server')
    remove_server_btns.forEach(i=>{
        i.addEventListener('click', clickServerConnect)
    })
}

listenToRemoveBtns()

function loadStart(panel){
    loading = document.querySelector(panel)
    $(loading).addClass('active')
    $(loading).css('overflow', 'hidden')
}

function loadStop(panel){
    loading = document.querySelector(panel)
    $(loading).removeClass('active')
    $(loading).css('overflow', 'auto')
}

let addServer = $('#addServer')
let discord_server_invite_link = $("input[name='discord_server_invite_link']")

addServer.click(function(event){
    event.preventDefault()
    
    loadStart('#serverAdding')

    // Create a string in serializable format and send with ajax
    let serverLink = 'discord_server_invite_link='+discord_server_invite_link[0].value

    let thisURL = window.location.href // or set your own url

    $.ajax({
        method: "POST",
        url: thisURL,
        data: serverLink,
        success: handleSuccess,
        error: handleError,
    })
})

function handleSuccess(data, textStatus, jqXHR){
    loadStop('#serverAdding')

    let message = data['message']
    data = data['object']

    // remover the no servers content
    try {
        $('#no_servers').remove()
    } catch (e) {
        
    }

    // Create element
    let e_tr = document.createElement('tr')
    let e_p = document.createElement('p')
    let e_img = document.createElement('img')
    let e_label = document.createElement('label')
    let e_btn_1 = document.createElement('button')
    let e_btn_2 = document.createElement('button')
    let e_td_name = document.createElement('td')
    let e_td_members = document.createElement('td')
    let e_td_buttons = document.createElement('td')

    e_img.src = data['icon']
    e_p.textContent = data['name']
    e_p.style.margin = '0px'
    e_p.style.display = 'inline'
    e_td_name.appendChild(e_img)
    e_td_name.appendChild(e_p)

    e_td_members.textContent = data['members']+' '
    e_label.className = 'avatar-icon'
    e_td_members.appendChild(e_label)

    e_btn_1.className = 'red'
    e_btn_2.classList.add('remove_server')
    e_btn_1.setAttribute('type', 'button')
    e_btn_1.textContent = 'Remove'

    e_btn_2.classList.add('green')
    e_btn_2.classList.add('connect_server')
    e_btn_2.setAttribute('type', 'button')
    e_btn_2.textContent = 'Connect'

    e_td_buttons.appendChild(e_btn_1)
    e_td_buttons.appendChild(e_btn_2)
    e_td_buttons.setAttribute('connect_uid', data['uid'])

    e_tr.appendChild(e_td_name)
    e_tr.appendChild(e_td_members)
    e_tr.appendChild(e_td_buttons)

    $('#server-list').append(e_tr)

    togglePopup(message)

    listenToConnectBtns()
}

function handleError(jqXHR, textStatus, errorThrown){
    loadStop('#serverAdding')

    let message = jqXHR['responseJSON']['message']
    togglePopup(message)
}


// Code to add blacklists
function upload(event) {
    event.preventDefault();
    var data = new FormData($('#blacklist-settings').get(0));
    
    loadStart('#blacklistAdding')
    $.ajax({
        url: window.location.href,
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: handleAddBlacklist,
        error: function (jqXHR) {
            loadStop('#blacklistAdding')

            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message)
        },
    });
    return false;
}

function handleAddBlacklist(data, textStatus, jqXHR){
    loadStop('#blacklistAdding')

    let message = data['message']
    data = data['object']

    // remover the no servers content
    try {
        $('#no_bl').remove()
    } catch (e) {
        
    }

    // Create element
    let e_tr = document.createElement('tr')
    let e_p = document.createElement('p')
    let e_img = document.createElement('img')
    let e_label = document.createElement('label')
    let e_btn_1 = document.createElement('button')
    let e_btn_2 = document.createElement('button')
    let e_td_name = document.createElement('td')
    let e_td_members = document.createElement('td')
    let e_td_buttons = document.createElement('td')

    e_img.src = 'https://www.clipartmax.com/png/small/246-2468580_blacklist-the-blacklist.png'
    e_p.textContent = data['name']
    e_p.style.margin = '0px'
    e_p.style.display = 'inline'
    e_td_name.appendChild(e_img)
    e_td_name.appendChild(e_p)

    e_td_members.textContent = data['members']+' '
    e_label.className = 'avatar-icon'
    e_td_members.appendChild(e_label)

    e_btn_1.className = 'red'
    e_btn_2.classList.add('remove_blacklist')
    e_btn_1.setAttribute('type', 'button')
    e_btn_1.textContent = 'Remove'

    e_btn_2.classList.add('green')
    e_btn_2.classList.add('select_blacklist')
    e_btn_2.setAttribute('type', 'button')
    e_btn_2.textContent = 'Select'

    e_td_buttons.appendChild(e_btn_1)
    e_td_buttons.appendChild(e_btn_2)
    e_td_buttons.setAttribute('blacklist_uid', data['uid'])

    e_tr.appendChild(e_td_name)
    e_tr.appendChild(e_td_members)
    e_tr.appendChild(e_td_buttons)

    $('#black_list').append(e_tr)

    togglePopup(message)

    // listenToConnectBtns()

    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';

    hideBlackListSettings();
}

let addBlacklistForm = document.querySelector('#blacklist-settings')
addBlacklistForm.addEventListener('submit', upload)

function confirmBlackListSettings(e) {
    // document.getElementById('blacklist-list').style.display = 'none';
    // document.getElementById('blacklist-settings').style.display = 'block';

    //Submits form to ajax
    $('#blacklist-settings').submit()

    // 
}