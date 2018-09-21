function init() {
    console.log("Page is loaded");
    try {
        authID = data.getResponseHeader('authorization');
        $("#query_form").submit(query_function);
    }
    catch(err) {
        console.log(err.message);
        $("#login_form").submit(login_function);
    }    
}

function logout(){
  $.ajax({
    url: "/logout", 
    type: 'DELETE',          
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', localStorage.getItem('authID'));
    },        
    complete : function(data){
        window.location.href ="/";
    }     
    });    
};

/* attach a submit handler to the form */

function login_function(event) {
  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

  $.ajax({
    url: "/user_login", 
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
            authID = data.getResponseHeader('authorization');
            localStorage.setItem('authID', authID);
            document.documentElement.innerHTML = data.responseText;
            document.getElementById("query_form").addEventListener("submit", query_function);
            document.getElementById("typeSel").addEventListener("change", on_sel);
            document.getElementById("logout").addEventListener("click", logout);
            on_sel();
        }
    }           
    });
}

function query_function(event) {
  /* stop form from submitting normally */
  event.preventDefault();

  /* get the action attribute from the <form action=""> element */
  var $form = $( this ),
      url = $form.attr( 'action' );

  $.ajax({
    url: "/query", 
    type: 'POST',          
    data: JSON.stringify({"type": $('#type').val(), 
                                   "match": $('#match').val(),
                                   "csrf_token": $('#csrf_token').val()
                                }),
    contentType: "application/json",
    dataType: "json",
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', localStorage.getItem('authID'));
    },            
    complete: function(data){
        if (data.status != 200) {
            alert(data.responseJSON['msg']);
            window.location.href ="/";
        }
        else {
            //console.log('query');
            authID = data.getResponseHeader('authorization');
        }
    }           
    });  
}

function on_sel(event) {
  $.ajax({
    url: "/get_match", 
    type: 'POST',          
    data: JSON.stringify({"type": $('#type').val(), 
                                   "csrf_token": $('#csrf_token').val()
                                }),
    contentType: "application/json",
    dataType: "json",
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', localStorage.getItem('authID'));
    },
    complete: function(data){
        if (data.status != 200) {
            alert(data.responseJSON['msg']);
            window.location.href ="/";
        }
        else {
            console.log(data.responseJSON);
            var matchSel = document.getElementById('matchSel');           
            matchSel.innerHTML = "";
            for (var i=0;i<data.responseJSON['match'].length;i++){
                var opt = document.createElement('option');
                opt.value = data.responseJSON['match'][i]['id'];
                opt.innerHTML = data.responseJSON['match'][i]['text'];
                matchSel.appendChild(opt);
            }
        }
    }
    });  
}


$(document).ready(function() {
  Ladda.bind( 'input[type=submit]' );
  var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
  $("#dateStart").datepicker({
    dateFormat: "mm/dd/yyyy",
    startDate: '01/01/2014',
    container: container,
    todayHighlight: true,
    autoclose: true,
  }).datepicker().on("changeDate", function(){
    populateEndDate();
  });
  $('#dateEnd').datepicker({
    dateFormat: "mm/dd/yyyy",
    startDate: '01/01/2014',
    container: container,
    todayHighlight: true,
    autoclose: true,    
  }).datepicker().on("changeDate", function(){
      var dt1 = $('#dateStart').datepicker('getDate');
      var dt2 = $('#dateEnd').datepicker('getDate');
      if (dt2 <= dt1) {
        $('#dateEnd').datepicker('setStartDate', dt1);
      }  
  });
  
    

});

    $("#btnSubmit").click(function(){
        var chkDTM=$('#chkDTM').prop('checked');
        var chknoDTM=$('#chknoDTM').prop('checked');
        var chkFinished=$('#chkFinished').prop('checked');
        var chkInProgress=$('#chkInProgress').prop('checked');
        var cmbType = $('#cmb1').prop('value'); 
        var cmbModel = $('#cmb2').prop('value'); 
        var from_date = $('#dateStart').prop('value');
        var to_date = $('#dateEnd').prop('value');        
        if ((!chkDTM && !chkNoDTM) || (cmbModel=="") || (!chkFinished && !chkInProgress)) {
            alert('Must select either Has DTM or No DTM or both, and either Finished or In Progress or both!!!');
            return;
        }
        var l = Ladda.create( this );
        l.start();
        $.ajax({
            url: "/genplot", 
            type: 'POST',
              beforeSend: function(request) {
                request.setRequestHeader("sessID", authID);
              },            
            data: JSON.stringify({"comboType": cmbType, 
                                   "comboModel": cmbModel,
                                   "from_date" : from_date,
                                   "to_date" : to_date,
                                   "chkDTM" : chkDTM,
                                   "chknoDTM" : chknoDTM,
                                   "chkFinished" : chkFinished,
                                   "chkInProgress" : chkInProgress,
                                }),
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                $('#fig').html(data['div']);
                l.stop();
            }
        });
    });

function OptChange(){
    var chkDTM=document.getElementById("chkDTM").checked;
    var chkNoDTM=document.getElementById("chknoDTM").checked;
    var chkFinished=document.getElementById("chkFinished").checked;
    var chkProgress=document.getElementById("chkInProgress").checked;
    var cmbModel = document.getElementById("cmb2").value; 
    if ((!chkDTM && !chkNoDTM) || (cmbModel=="") || (!chkFinished && !chkProgress)) {
        //alert('Must select either Has DTM or No DTM or both, and either Finished or In Progress or both!!!');
        $('#btnSubmit').prop('disabled', true);
        $('#btnReport').prop('disabled', true);
    }
    else {
        $('#btnSubmit').prop('disabled', false);
        $('#btnReport').prop('disabled', false);
    }
};

function populateEndDate() {
  var date2 = $('#dateStart').datepicker('getDate');
  date2.setDate(date2.getDate() + 1);
  $('#dateEnd').datepicker('setDate', date2);
  $("#dateEnd").datepicker("setStartDate", date2);
}