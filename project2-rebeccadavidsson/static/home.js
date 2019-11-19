document.addEventListener('DOMContentLoaded', () => {

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // If the user was in a room before they left, send them back to that room
  if (localStorage.getItem('channel')) {
    socket.emit("join_channel", localStorage.getItem('channel'));
  }
  else {
    socket.emit("join_channel", "")
  }


  // Only make request when user submits the form
  document.querySelector('#form').onsubmit = () => {

    // Make a new AJAX request
    const request = new XMLHttpRequest();

    // Get username and add to data
    const username = document.querySelector('#username').value;

    // Handle response when request is done being loaded
    request.onload = () => {
      const data = JSON.parse(request.responseText);

      document.querySelector('#form').style.display = 'none';

      if (data.succes) {

        setTimeout(function () {
          location.reload();
        }, 1000);

        // Add new element to welcome user.
        var content  = "<h3> " + 'Welcome ' + username + '!' + "</h3>" + "<h4>" + 'Loading page...' + "</h4>";
        // location.reload();
      }
      else {
        var content  = "<h3> " + 'There was an error!' + "</h3>";
      }

      // Change innerHTML content of div
      document.querySelector('div.card-header').innerHTML = content;
    }

    // Add data to send with request
    const data = new FormData();
    data.append('username', username);

    // Open the created request and send data
    request.open('POST', '/username');
    request.send(data);

    // Clear local storage at the moment that user registers
    localStorage.clear();

    return false;
  }

  // Create new channel when channelbutton is pressed
  document.querySelector('#createchannel').onsubmit = () => {
    const channel = document.querySelector('#createchannelinput').value;
    socket.emit('createchannel', channel);

    document.querySelector('#createchannel').reset();
    return false;
  };

  // Emit a new message on 'send' button
  document.querySelector('#messageform').onsubmit = () => {
      const message = document.querySelector('#message').value;
      socket.emit('new_message', {'message': message,
                  "channel": localStorage.getItem('channel')});

      // Clear submit form
      document.querySelector('#messageform').reset();
      return false;
    };


  // When a new message is sent, add to list of messages
  // 'push message' is called in application.py
  socket.on("push_message", data => {
    const li = document.createElement('li');
    li.innerHTML = `<span class="dotchat"></span><strong>   ${data.username}:</strong> ${data.message} <small>(${data.time})</small>`;
    document.querySelector('#messages').append(li);
  });


  socket.on("join_channel", data => {



    // Check if user has already created a channel
    if (data["channel"] == ""  && localStorage.getItem('channel') == null) {
      document.querySelector('#messagescontainer').style.display = 'none';
    }
    else {

      // Save the channel in the user's memory
      localStorage.setItem('channel', data["channel"]);

      // Display messages screen
      document.querySelector('#messagescontainer').style.display = 'block';
    }


    // Check if a new channel has to be created
    if (data["add"] == true) {
      if (data["first"] == false) {
        for (var i in data["allchannels"]) {

          // Load content of all channels
          loadContent(data["allchannels"][i])
        }
      }
      else {
        loadContent(data["channel"])
      }
    }
    else {

      // Channel already exists
      alert("You joined an existing channel: " + data["channel"])
    }


  // Load content of channel(s) on page
  function loadContent(disp) {

    // Create new element to add to table
    const tr = document.createElement('tr');
    tr.innerHTML = `<tr > <td> <button class="btn btn-light" onclick="join()" id=${disp}> ${disp} </button> </td> </tr>`;

    // Select list of channels in HTML
    document.querySelector('#channelstable').append(tr)

    // Change header to current channel (select element in HTML)
    document.querySelector("#channelheader").innerHTML = "Current channel: " + data["channel"]

  }

  // Clear the messages area
  document.querySelector("#messages").innerHTML = "";

  if (data["messages"]) {
    // Get every message to display in a new li-element
    for (var x in data["messages"]) {
        const li = document.createElement('li');
        li.innerHTML = `<span class="dotchat"></span><strong>   ${data["messages"][x].username}:</strong> ${data["messages"][x].message} <small>(${data["messages"][x].time})</small>`;
        document.querySelector("#messages").append(li);
    }
  }

  // Change header to current channel (select element in HTML)
  document.querySelector("#channelheader").innerHTML = "Current channel: " + data["channel"]
  return false;

  });
});
