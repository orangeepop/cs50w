document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  //send email
  document.querySelector('#compose-form').onsubmit = send_email;
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#emails-table').innerHTML = '';
  document.querySelector('#email').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
};

async function edit_email(id, parameter, value) {
  return await fetch(`/emails/${id}`, {
    method: 'PUT',
    body: `{"${parameter}":${value}}`
  });
};

function reply_email(email) {
  //reply email
  reply = document.createElement('button');
  reply.type = 'button';
  reply.className = 'btn btn-light';
  reply.innerHTML = 'Reply';
  reply.addEventListener('click', function(){
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email').innerHTML = '';

    // prefill composition fields
    document.querySelector('#compose-recipients').value = `${email.sender}`;
    if (email.subject.slice(0, 4).indexOf("Re: ") < 0) {
      //Re: not found ie. not already a reply
      document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    } else {
      //Re: found; ie. is a reply, do not add Re:
      document.querySelector('#compose-subject').value = `${email.subject}`;
    };
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
  })
  return reply
};

function archive_email(email) {
  //archive button
  arc = document.createElement("button");
  arc.type = 'button';
  arc.className = 'btn btn-light';

  if (email.archived == true) {
    arc.innerHTML = 'Unarchive';
  } else {
    arc.innerHTML = 'Archive';
  };

  //archive email on click
  arc.addEventListener('click', async function() {
    await edit_email(email.id, 'archived', !email.archived)

    //redirect to inbox once archive button is clicked
    load_mailbox('inbox');
  });

  //return archive button element
  return arc;
};

function generate_email_head(email) {
  let email_head = document.createElement('div');
  let from = `<b>From:</b> ${email.sender}<br>`;
  let to = `<b>To:</b> ${email.recipients}<br>`;
  let subject = `<b>Subject:</b> ${email.subject}<br>`;
  let timestamp = `<b>Textstamp:</b> ${email.timestamp}<b>`;
  email_head.innerHTML = from + to + subject + timestamp
  return email_head;
};


function generate_email_body(email) {
  let email_body = document.createElement('div');
  email_body.innerHTML = `${email.body}`;
  return email_body;
}

async function mailbox_html(emails, to_from, sender_recipients, mailbox) {
  //create table for displaying emails
  var table = document.createElement('table');
  table.className="table";
  var thead = document.createElement('thead');
  var head_tr = document.createElement('tr');
  var head_th1 = document.createElement('th');
  head_th1.scope = 'col';
  head_th1.innerHTML = `${to_from}`;
  var head_th2 = document.createElement('th');
  head_th2.scope = 'col';
  head_th2.innerHTML = 'Subject';
  var head_th3 = document.createElement('th');
  head_th3.scope = 'col';
  head_th3.innerHTML = 'Time';
  head_tr.appendChild(head_th1);
  head_tr.appendChild(head_th2);
  head_tr.appendChild(head_th3);
  thead.appendChild(head_tr);
  table.appendChild(thead);
  var tbody = document.createElement('tbody');

  //generate html elements as rows and cells of emails table
  await emails.forEach(async function(email){
    let email_element = document.createElement('tr');
    row_html = ''
    if (email.read === true) {
      email_element.className="table-primary"
    }
    if (sender_recipients === 'sender') {
      row_html += `<th scope="row">${email.sender}</th>`
    } else {
      row_html += `<th scope="row">${email.recipients}</th>`
    };
    row_html += `<td>${email.subject}</td>
    <td>${email.timestamp}</td>`;
    email_element.innerHTML = row_html;
    tbody.appendChild(email_element);

    //generate email view when email row is clicked
    email_element.addEventListener('click', function() {
      fetch(`/emails/${email.id}`)
      .then(response => response.json())
      .then(email_content => {
        //erase emails table
        document.querySelector('#emails-table').innerHTML = '';
        
        //mark email as read when clicked
        edit_email(email.id, 'read', true);

        //generate html elements for displaying contents of email
        email_head = generate_email_head(email_content)
        email_body = generate_email_body(email_content)
        document.querySelector('#email').appendChild(email_head);
        
        //reply email
        reply = reply_email(email_content);
        document.querySelector('#email').appendChild(reply);

        //generate archive button if not in sent inbox
        if (mailbox != 'sent') {
          archive = archive_email(email_content);
          document.querySelector('#email').appendChild(archive);
        }
        document.querySelector('#email').appendChild(email_body);
      });
    });
  table.appendChild(tbody);
  document.querySelector('#emails-table').appendChild(table);
  });
};

async function load_mailbox(mailbox) {
  document.querySelector('#emails-table').innerHTML = '';
  document.querySelector('#email').innerHTML = '';
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  html = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  //populate html based on mailbox
  const res = await fetch(`/emails/${mailbox}`);
  const emails = await res.json();

  if (mailbox === 'sent') {
    await mailbox_html(emails, 'To', 'recipients', mailbox)
  } else if (mailbox === 'inbox') {
    await mailbox_html(emails, 'From', 'sender', mailbox)
  } else if (mailbox === 'archive') {
    archived_emails = []
    emails.forEach(function(email) {
      if (email.archived === true) {
        archived_emails.push(email);
      };
    });
    await mailbox_html(archived_emails, 'From', 'sender', mailbox)
  };

  document.querySelector('#emails-view').innerHTML = html;
};

function send_email() {
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;
  // console.log(recipients, subject, body);
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  load_mailbox('sent');
  return false;
};