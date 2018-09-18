$(function(){
    $("#btnSubmit").click(function(){
        $.ajax({
            url: "/login", 
            type: 'POST',          
            data: JSON.stringify({"username": $('#username').val(), 
                                   "password": $('#password').val()
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

/* attach a submit handler to the form */
$("#formoid").submit(function(event) {

  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

  /* Send the data using post with element id name and name2*/
  var posting = $.ajax({
            url: "/user_login", 
            type : 'POST',
            data: JSON.stringify({"username": $('#username').val(), 
                                   "password": $('#password').val()
                                }),
            contentType: "application/json",
            dataType: "json",
            complete: function(data){
                alert('hi');
                console.log('hi');
            }            
            });
});