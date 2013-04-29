function custom_error(){
    // do nothing
}

/*****************************************************************************************
/* User Profile
*/

function selectUserProfile(value) {
	$("#message").html("");
    Dajaxice.accounts.getUserProfile(showUserProfile, {'pk': value}, {'error_callback': custom_error}); 		       
}

function uptest(value) {
	alert(value);
}

function showUserProfile(data) {
	if(data.success == "true") {
		$('#firstname').val(data.first_name);
		$('#lastname').val(data.last_name);
		$('#addr').val(data.addr);
		$('#phone').val(data.phone);
		$('#description').val(data.description);
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}






