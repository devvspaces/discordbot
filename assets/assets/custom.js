// Adding the format attr to strings
String.prototype.format = function () {
    var i = 0, args = arguments;
    return this.replace(/{}/g, function () {
      return typeof args[i] != 'undefined' ? args[i++] : '';
    });
  };

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

try{

    delay.oninput = function() {
        delay_display.innerHTML = delay.value + 's';
    }
} catch(e){
    
}

function showBlackListSettings() {
    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';
}
function hideBlackListSettings() {
    document.getElementById('blacklist-list').style.display = '';
    document.getElementById('blacklist-settings').style.display = '';
}


// Codes for popup messages
let popup = $('.popup')
function togglePopup(message, time=5000){
    popup.addClass('active')
    popup[0].lastElementChild.innerHTML = message
    setTimeout(() => {
        popup.removeClass('active')
    }, time);
}

// Close popup
$('.popup .close').on('click', function(){
    $(this.parentElement).removeClass('active')
})

let connect_server_btns = document.querySelectorAll('.connect_server')
let remove_server_btns = document.querySelectorAll('.remove_server')

// Clicking connect_server_btn and remove server event ajax
function clickServerConnect(e) {
    // GEt the connect uid
    e.preventDefault()
    connect_id = e.target.parentElement.getAttribute('connect_id')
    let parent = e.target.parentElement.parentElement

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


    // If the user is trying to connect the server again, decline
    if ((req_type == 'connect') && $(parent).hasClass('selected')) {
        $(parent).removeClass('selected')
        e.target.innerText = 'Connect'
        return
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
                parent.remove()
            } else if(req_type=='connect'){
                // Change the color and text for the button
                if ($(parent).hasClass('selected')){
                    $(parent).removeClass('selected')
                    e.target.innerText = 'Connect'
                } else {
                    $(parent).addClass('selected').siblings().removeClass('selected')
                    $('.connect_server').text('Connect')
                    e.target.innerText = 'Connected'
                }
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
// function listenToRemoveBtns() {
//     remove_server_btns = document.querySelectorAll('.remove_server')
//     remove_server_btns.forEach(i=>{
//         i.addEventListener('click', clickServerConnect)
//     })
// }

// listenToRemoveBtns()


function loadStart(panel){
    loading = document.querySelector(panel)
    $(loading).addClass('active')
    $(loading).css('overflow', 'hidden')
}

function loadStop(panel){
    loading = document.querySelector(panel)
    $(loading).removeClass('active')
    $(loading).css('overflow', 'initial')
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

    // Create server element
    let name = data['name']
    let uid = data['uid']
    let icon = data['icon']
    let members = data['members']
    let url = data['url']

    let new_html = `<tr>
                        <td class="icon_name_side"><img src="{}" alt=""><a href="{}">{}</a></td>
                        <td>{} <label class="avatar-icon"></label></td>
                        <td class="actions" connect_id="{}"><a href="{}" class="btn btn-teal">Open</a><button class="btn btn-teal connect_server">Connect</button></td>
                    </tr>`.format(icon, url, name, members, uid, url)
    
    console.log(data)

    let server_list = $('#server-list')
    server_list.html(server_list.html()+new_html)

    togglePopup(message)

    // Add event listeners to the new buttons created
    listenToConnectBtns()
    // listenToRemoveBtns()


    // Create manage element
    let new_manage = `<tr>
        <td class="manage_select"><span uid="{}"></span></td>
        <td class="icon_name_side"><img src="{}" alt=""><a href="{}">{}</a></td>
        <td>{} <label class="avatar-icon"></label></td>
    </tr>`.format(uid, icon, url, name, members)

    $('#manage_list').html($('#manage_list').html()+new_manage)
    listenToManageSelectors()
}

function handleError(jqXHR, textStatus, errorThrown){
    loadStop('#serverAdding')

    let message = jqXHR['responseJSON']['message']
    togglePopup(message)
}


// Code to add blacklists
function blacklistUpload(event) {
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

// Ajax to remove blacklist
function blacklistRemove(e) {
    e.preventDefault()

    // Confirm user wants to remove server
    let confimation = confirm("Are you sure to remove this blacklist?")

    if (confimation == false){
        return
    }
    
    let blacklist = e.target.parentElement
    blacklist_uid = blacklist.getAttribute('blacklist_uid')

    // Create a string in serializable format and send with ajax
    let postData = 'blacklist_uid='+blacklist_uid

    let thisURL = window.location.href // or set your own url

    loadStart('#blacklistAdding')

    $.ajax({
        method: "POST",
        url: thisURL,
        data: postData,
        success: function (data){
            loadStop('#blacklistAdding')

            // Remove the removed blacklist
            $(blacklist).parent().fadeOut()

            setTimeout(function(){
                $(blacklist).parent().remove()
            }, 1500)

            // Get message display on popup
            message = data['message']
            togglePopup(message)
        },
        error: function (jqXHR) {
            loadStop('#blacklistAdding')

            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message)
        },
    })
}

// Code for remove_server
function listenRemoveBlacklist() {
    remove_blacklist_btns = document.querySelectorAll('.remove_blacklist')
    remove_blacklist_btns.forEach(i=>{
        i.addEventListener('click', blacklistRemove)
    })
}

// listenRemoveBlacklist()


function handleAddBlacklist(data, textStatus, jqXHR){
    loadStop('#blacklistAdding')

    let message = data['message']
    data = data['object']

    // remover the no servers content
    try {
        $('#no_bl').remove()
    } catch (e) {
        
    }

    // Create 
    let name = data['name']
    let uid = data['uid']
    let icon = data['icon']
    let members = data['members']
    let url = data['url']

    let new_html = `<tr>
        <td><img src="https://www.clipartmax.com/png/small/246-2468580_blacklist-the-blacklist.png"><a href="{}">{}</a></td>
        <td>{} <label class="avatar-icon"></label></td>
        <td class="actions" blacklist_uid="{}"><a href="{}" class="btn btn-teal">Open</a><button class="btn btn-teal select_blacklist" type="button" onclick="">Select</button></td>
    </tr>`.format(url, name, members, uid, url)

    let black_list = $('#black_list')
    black_list.html(black_list.html()+new_html)

    togglePopup(message)

    // listenRemoveBlacklist()
    listenSelectBlacklist()

    document.getElementById('blacklist-list').style.display = 'none';
    document.getElementById('blacklist-settings').style.display = 'block';

    hideBlackListSettings();
}

let addBlacklistForm = document.querySelector('#blacklist-settings')
try {
    addBlacklistForm.addEventListener('submit', blacklistUpload)
} catch (error) {
    
}

function confirmBlackListSettings(e) {
    //Submits form to ajax
    $('#blacklist-settings').submit()
}


// Block of codes for selecting blacklists

// Event listener to select blacklist
function blacklistSelect(e) {
    let parent = e.target.parentElement.parentElement

    // Change the color and text for the button
    if ($(parent).hasClass('selected')){
        $(parent).removeClass('selected')
        e.target.innerText = 'Select'
    } else {
        $(parent).addClass('selected').siblings().removeClass('selected')
        $('#blacklist-list .select_blacklist').text('Select')
        e.target.innerText = 'Selected'
    }
}
// Code to select and unselect a blacklist
function listenSelectBlacklist() {
    select_blacklist_btns = document.querySelectorAll('#blacklist-list .select_blacklist')
    select_blacklist_btns.forEach(i=>{
        i.addEventListener('click', blacklistSelect)
    })
}

listenSelectBlacklist()


// Event to start message sending
function textLoad(val){
    $('#startstop').html(val)
}
function start(e) {
    let target = e.target
    
    // Check to see if it is running or not
    if ($(target).hasClass('active')){
        // Stop the server here
        uid = target.getAttribute('uid')
        if (uid){
            // Send to the server here
            // Create a string in serializable format and send with ajax
            let postData = 'stop_message={}'.format(uid)

            let thisURL = window.location.href // or set your own url

            togglePopup('Stopping messages ...', time=2000)

            
            textLoad('<div class="loading"></div>')

            $.ajax({
                method: "POST",
                url: thisURL,
                data: postData,
                success: function (data){
                    // Get message display on popup
                    message = data['message']
                    togglePopup(message)

                    $(target).removeClass('active')
                    textLoad('Start')
                    target.removeAttribute('uid')
                },
                error: function (jqXHR) {
                    // Get message display on popup
                    let message = jqXHR['responseJSON']['message']
                    togglePopup(message, time=10000)

                    textLoad('Stop')
                },
            })
        }

        return
    }

    // Get the data to send
    let blacklist_selected = document.querySelector('#black_list .selected')
    let blacklist_uid = ''
    if (blacklist_selected != null){
        blacklist_uid = blacklist_selected.querySelector('.select_blacklist').parentElement.getAttribute('blacklist_uid')
    }

    let server_selected = document.querySelector('#server-list .selected')
    let connect_uid = ''
    if (server_selected != null){
        connect_uid = server_selected.querySelector('.connect_server').parentElement.getAttribute('connect_id')
    }

    let direct_message = $('#direct_message').val()

    let stop_after_amount = $("input[name='stop_after_amount']").val()
    
    let add_friend_checkbox = $('#add_friend_checkbox')[0].checked

    let add_to_blacklist_checkbox = $('#add_to_blacklist_checkbox')[0].checked

    let delay = $('#delay').val()

    // Validate the data to be sent
    let valid = true
    let validation_message = []

    if (direct_message == ''){
        validation_message.push('You can\'t send an empty message')
        valid = false
    }

    if (parseInt(delay) < 15){
        validation_message.push('Your delay can\'t be less than 15')
        valid = false
    }

    if (isNaN(parseInt(stop_after_amount))){
        validation_message.push('Your stop after input must be a number')
        valid = false
    }

    if (connect_uid == ''){
        validation_message.push('You have to connect one discord server')
        valid = false
    }


    // If valid send
    if (valid){
        // Send to the server here
        // Create a string in serializable format and send with ajax
        let postData = 'send_dm=true&connect_uid={}&blacklist_uid={}&direct_message={}&stop_after_amount={}&add_friend_checkbox={}&add_to_blacklist_checkbox={}&delay={}'.format(connect_uid, blacklist_uid, direct_message, stop_after_amount, add_friend_checkbox, add_to_blacklist_checkbox, delay)

        let thisURL = window.location.href // or set your own url

        togglePopup('Starting to send messages ...', time=2000)

        $(target).html('<div class="loading"></div>')

        $.ajax({
            method: "POST",
            url: thisURL,
            data: postData,
            success: function (data){
                // Get message display on popup
                message = data['message']
                togglePopup(message)

                textLoad('Stop')
                $(target).addClass('active')
                target.setAttribute('uid', data['message_uid'])
            },
            error: function (jqXHR) {
                // Get message display on popup
                let message = jqXHR['responseJSON']['message']
                togglePopup(message, time=10000)

                textLoad('Start')
            },
        })
    } else {
        togglePopup(validation_message.join('<br>'), time=10000)
    }

    
}

let startstop = document.querySelector('#startstop')
try {
    startstop.addEventListener('click', start)
} catch (error) {
    
}



// Websocket messages
let chatSocket = ''
try {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/webchat/'
        + roomName
        + '/'
    );

    let m_left = document.getElementById('m_left')
    let m_sent = document.getElementById('m_sent')
    let m_total = document.getElementById('m_total')
    let progress_count = document.getElementById('progress_count')

    function updateProgress() {
        progress_count.value = (parseInt(m_sent.innerText)/parseInt(m_total.innerText))*100
    }
    updateProgress()

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        let startstop = document.getElementById('startstop')

        if (data.type == 'message_update'){
            let count = parseInt(data.count);
            m_left.innerText = parseInt(m_left.innerText) - count
            m_sent.innerText = parseInt(m_sent.innerText) + count
            updateProgress()
        } else if (data.type == 'completed_message'){
            $(startstop).removeClass('active')
            textLoad('Start')
            startstop.removeAttribute('uid')
        }
        
        if (data.message.length > 0){
            togglePopup(data.message)
        }
    };

    chatSocket.onclose = function(e) {
        console.error('UI Bad Response');
        location.reload()
    };
} catch (error) {
    
}


// Code to open and close blacklist
$('.modal_open').on('click', function () {
    $(this.getAttribute('modal')).addClass('active')
})
$('.modal_close').on('click', function () {
    $(this.getAttribute('modal')).removeClass('active')
})



// Code to select and unselect a blacklist in the server detail view
function IsBlackListSelected(){
    let bb = $('#blacklistbox .item.selected')
    try{
        // Means an item as been selected
        $('#blacklist_indicator').text(bb.children()[0].innerText)
        return true
    } catch (e) {
        $('#blacklist_indicator').text('No blacklist selected')
        return false
    }
}
$('#blacklistbox .select_blacklist').on('click', function(){
    $(this.parentElement).toggleClass('selected').siblings().removeClass('selected')
    IsBlackListSelected()
})

// Code to search for items in the body
let userNames = document.querySelectorAll('#server .table tbody tr')
$('#search_input').on('keyup', function () {
    userNames.forEach(i=>{
        // Check for the searches
        // 1. Username
        let children = i.children
        if (children[1].innerText.toLowerCase().indexOf($('#search_input').val().toLowerCase()) == -1){
            $(i).fadeOut()
        } else {
            $(i).fadeIn()
        }
    })
})


// Removing the item
function removeItem(btn) {
    let item = btn.parentElement.parentElement.parentElement
    let uid = item.getAttribute('uid')
    $(item).fadeOut()

    // Reduce user count
    $('#user_count').text(parseInt($('#user_count').text())-1)

    setTimeout(function () {
        item.remove()
    }, 300)
    return uid
}

// Ajax delete the user or and also add to blacklist
function deleteItemUser(uid, blacklist=false, blacklist_uid='') {
    // Create a string in serializable format and send with ajax
    let postData = 'blacklist={}&uid={}&blacklist_uid={}'.format(blacklist, uid, blacklist_uid)

    let thisURL = window.location.href // or set your own url

    $.ajax({
        method: "POST",
        url: thisURL,
        data: postData,
        success: function (data){
            // Get message display on popup
            message = data['message']
            togglePopup(message)

            if (blacklist){
                // Update the blacklist user count
                let blacklist_count = $("#blacklistbox .item[uid='{}'] .blacklist_count".format(blacklist_uid))
                blacklist_count.text(parseInt(blacklist_count.text()) + 1)
            }
        },
        error: function (jqXHR) {
            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message, time=10000)
        }
    })
}

// Code to remove user from the dm list
$('#server table tbody tr .remove_user').on('click', function(){
    let val = confirm('Do you really want to remove this user?')
    if (val){
        deleteItemUser(removeItem(this))
    }
})

// Code to add user to blacklist and remove from dm list
$('#server table tbody tr .add_to_blacklist').on('click', function(){
    if (IsBlackListSelected() == false){
        togglePopup('Please do select a blacklist to add the user to first!')
        return
    }
    let val = confirm('Do you really want to add this user to blacklist?')
    if (val){
        deleteItemUser(removeItem(this), blacklist=true, blacklist_uid = $('#blacklistbox .item.selected').attr('uid'))
    }
})


// Code to remove blacklist from the blacklist detail page
$('#server table tbody tr .del_blacklist').on('click', function(){
    let val = confirm('Do you really want to remove this user from this blacklist?')
    if (val){
        deleteItemUser(removeItem(this))
    }
})

// Code to manage servers in the dm panel
$('#manageServers').on('click', function () {
    $('#manageServers').toggleClass('active')

    if ($('#manageServers').hasClass('active')){
        $('#slide1').css('display', 'none')
        $('#slide2').css('display', 'block')
        $('#manageServers').text('Close')
    } else {
        $('#slide2').css('display', 'none')
        $('#slide1').css('display', 'block')
        $('#manageServers').text('Manage Servers')
    }
})

function checkManageSelected() {
    let sels = document.querySelectorAll('.manage_select span.active')
    if (sels.length > 0){
        $('#manage_server_box').addClass('active')
    } else {
        $('#manage_server_box').removeClass('active')
    }

    $('#servers_selected_p').text(sels.length)

    return sels
}

// Code to select and deselect servers for managing
function listenToManageSelectors() {
    $('.manage_select span').on('click', function(){
        $(this).toggleClass('active')
    
        // Check for if any selected
        checkManageSelected()
    })    
}
listenToManageSelectors()

// Code to delete the selected servers when managing
$('#dss_manage').on('click', function(){
    let sels = checkManageSelected()


    console.log(sels)

    let uids = []
    sels.forEach(i=>{
        uids.push(i.getAttribute('uid'))
    })

    // Create a string in serializable format and send with ajax
    let postData = 'delete_uid={}'.format(uids.join('|'))

    let thisURL = window.location.href // or set your own url

    $.ajax({
        method: "POST",
        url: thisURL,
        data: postData,
        success: function (data){
            // Get message display on popup
            message = data['message']
            togglePopup(message)

            sels.forEach(i=>{
                let parent = i.parentElement.parentElement
                $(parent).fadeOut()
                setTimeout(function(){
                    parent.remove()
                    checkManageSelected()
                }, 1000)
                // Find the server list items with this uid
                let val = $("#server-list tr td[connect_id={}]".format(i.getAttribute('uid'))).parent()
                console.log(val)
                val.remove()
            })

        },
        error: function (jqXHR) {
            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message, time=10000)
        }
    })
})



// Code to display and undisplay password in add_account
$('#eye_visible').on('click', function(){
    let val = $(this)
    val.toggleClass('active')
    if (val.hasClass('active')){
        $('#'+this.getAttribute('input')).attr('type', 'text')
    } else {
        $('#'+this.getAttribute('input')).attr('type', 'password')
    }
})


// Code to submit update server form
$("#update_server button[type='submit']").on('click', function(event){
    event.preventDefault();
    
    // Get the form
    let form = document.querySelector('#update_server form')
    var data = new FormData($(form).get(0));
    
    console.log(data)

    $.ajax({
        url: window.location.href,
        type: $(form).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data){
            // Get message display on popup
            message = data['message']
            togglePopup(message)
        },
        error: function (jqXHR) {
            // Get message display on popup
            let message = jqXHR['responseJSON']['message']
            togglePopup(message)
        },
    });
})