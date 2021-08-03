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

// Clicking connect_server_btn
function clickServerConnect(e) {
    // GEt the connect uid
    e.preventDefault()
    connect_id = e.target.getAttribute('connect_id')
    
    loadStart()

    // Create a string in serializable format and send with ajax
    let serverLink = 'connect_id='+connect_id

    let thisURL = window.location.href // or set your own url

    $.ajax({
        method: "POST",
        url: thisURL,
        data: serverLink,
        success: function (data, textStatus, jqXHR){
            loadStop()
            
            // Get message display on popup
            message = data['message']
            togglePopup(message)
        },
        error: handleError,
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

let loading = $('#loading')

function loadStart(){
    loading.addClass('active')
    $('body').css('overflow', 'hidden')
    $('#sidenav').css('filter', 'blur(12px)')
    $('#board').css('filter', 'blur(12px)')
    $('nav').css('filter', 'blur(12px)')
}

function loadStop(){
    loading.removeClass('active')
    $('body').css('overflow', 'auto')
    $('#sidenav').css('filter', 'blur(0)')
    $('#board').css('filter', 'blur(0)')
    $('nav').css('filter', 'blur(0)')
}

let serverList = $('#server-list')
let noServers = $('#no_servers')
let addServer = $('#addServer')
let discord_server_invite_link = $("input[name='discord_server_invite_link']")

addServer.click(function(event){
    event.preventDefault()
    
    loadStart()

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


// function handleRedirect(data, textStatus, jqXHR){
// 	console.log(data)
//     console.log(textStatus)
//     console.log(jqXHR)
//     // Get redirect information and change windows location
//     redirect = data['redirect']
//     window.location.href = 'http://'+redirect
// }

function handleSuccess(data, textStatus, jqXHR){
    loadStop()

    let message = data['message']
    data = data['object']

    // remover the no servers content
    try {
        noServers.remove()
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
    e_btn_1.setAttribute('type', 'button')
    e_btn_1.textContent = 'Remove'
    e_btn_2.className = 'green'
    e_btn_2.setAttribute('type', 'button')
    e_btn_2.textContent = 'Connect'
    e_td_buttons.appendChild(e_btn_1)
    e_td_buttons.appendChild(e_btn_2)

    e_tr.appendChild(e_td_name)
    e_tr.appendChild(e_td_members)
    e_tr.appendChild(e_td_buttons)

    serverList.append(e_tr)

    togglePopup(message)

    listenToConnectBtns()
}

function handleError(jqXHR, textStatus, errorThrown){
    loadStop()

    let message = jqXHR['responseJSON']['message']
    togglePopup(message)

    console.log(jqXHR)
}