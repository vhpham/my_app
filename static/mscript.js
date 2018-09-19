$(function(){
    $("#btnSubmit").click(function(){
        $.ajax({
            url: "/", 
            type: 'POST',          
            data: JSON.stringify({"username": $('#username').val(), 
                                   "password": $('#password').val(),
                                   "csrf_token": $('#csrf_token').val()
                                }),
            contentType: "application/json",
            dataType: "json",
            complete: function(data){
                if (data.status != 200) {
                    alert(data.responseJSON['msg']);
                }
                else {
                    console.log('hi');
                }
            }
        });
        
    }); 
});


var authID = 'Bearer ';
/* attach a submit handler to the form */
//$("#myform").submit(function(event) {
$("#submit").on('click',function(e)    {
  alert( "Handler for .submit() called." );
  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

  if ($("#login").length>0) {
  /* Send the data using post with element id name and name2*/
  var posting = $.ajax({
    url: url, 
    type: 'POST',          
    data: JSON.stringify({"username": $('#username').val(), 
                                   "password": $('#password').val(),
                                   "csrf_token": $('#csrf_token').val()
                                }),
    contentType: "application/json",
    dataType: "json",        
    complete: function(data){
        if (data.status != 200) {
            alert(data.responseJSON['msg']);
            authID = 'Bearer ';
        }
        else {
            console.log('login');
            authID = data.getResponseHeader('authorization');
            var d = jQuery(data.responseText);
            for (var i=0;i<d.length;i++){
                if (d[i].className == "container")
                {
                    console.log('change innerHTML');
                    document.getElementById('container').outerHTML = d[i].outerHTML;
                }
            }
            
        }
    }           
    });

  }
  else {
  /* Send the data using post with element id name and name2*/
  var posting = $.ajax({
    url: url, 
    type: 'POST',          
    data: JSON.stringify({"type": $('#type').val(), 
                                   "match": $('#match').val(),
                                   "csrf_token": $('#csrf_token').val()
                                }),
    contentType: "application/json",
    dataType: "json",
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + authID);
    },            
    complete: function(data){
        if (data.status != 200) {
            alert(data.responseJSON['msg']);
            authID = 'Bearer ';
        }
        else {
            console.log('query');
            authID = data.getResponseHeader('authorization');
            document.documentElement.innerHTML = data.responseText;
        }
    }           
    });  
  }    
});