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


var authID = '';
/* attach a submit handler to the form */
$("#myformlogin").submit(function(event) {
  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

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
            authID = '';
        }
        else {
            console.log('login');
            authID = data.getResponseHeader('authorization');
            document.documentElement.innerHTML = data.responseText;
            eval(document.getElementById("myjs").innerHTML);
            //$.ajax({
            //    url: url, 
            //    type: 'GET',          
            //    beforeSend: function(xhr) {
            //        xhr.setRequestHeader('Authorization', authID);
            //    },            
            //    complete: function(data){
            //        if (data.status != 200) {
            //            alert(data.responseJSON['msg']);
            //            //authID = 'Bearer ';
            //        }
            //        else {
            //            console.log('query');
            //            //authID = data.getResponseHeader('authorization');
            //            document.documentElement.innerHTML = data.responseText;
            //        }
            //    }           
            //    }); 
            
        }
    }           
    });
});

//function myFunction(){

$("#myformquery").submit(function(event) {
  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

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
        xhr.setRequestHeader('Authorization', authID);
    },            
    complete: function(data){
        if (data.status != 200) {
            alert(data.responseJSON['msg']);
            console.log(authID);
        }
        else {
            console.log('query');
            authID = data.getResponseHeader('authorization');
            document.documentElement.innerHTML = data.responseText;
            eval(document.getElementById("myjs").innerHTML);
        }
    }           
    });  
});
//}