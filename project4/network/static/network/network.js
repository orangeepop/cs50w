document.addEventListener('DOMContentLoaded', function() {
    // edit button
    button = document.createElement('button');
    button.className = 'btn btn-light btn-sm';
    button.innerHTML= 'Edit'
    var id = "{{ post.id }}"
    
    //add button to post
    br = document.createElement('br');
    document.querySelector(`[id='${id}']`).appendChild(br);
    document.querySelector(`[id='${id}']`).appendChild(button);


    //when button is clicked, post content may be edited
    button.addEventListener('click', function() {
        //erase existing post and replace with form and textarea
        document.querySelector(`[id='${id}']`).innerHTML = ''
        form = document.createElement('form');
        form.action = "{% url 'index' %}"
        form.method = "post"
        form.innerHTML = '{% csrf_token %}'

        text = document.createElement('textarea');
        text.innerHTML = '{{ post.post }}'
        text.className = 'form-control'
        text.name = 'edit-post'
        form.appendChild(text);

        submit = document.createElement('button');
        submit.innerHTML = 'Save'
        submit.className = 'btn btn-light btn-sm'
        submit.type = 'submit'
        submit.name = 'id'
        submit.value = id
        form.appendChild(submit);

        document.querySelector(`[id='${id}']`).appendChild(form);
    })  
})