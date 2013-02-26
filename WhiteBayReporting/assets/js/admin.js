function custom_error(){
    // do nothing
}

function selectBroker(value) {
	$("#message").html("");
	if(value == "default") {
		$('#mod_broker').hide();
		$('#add_broker').hide();
		return ;
	} else if(value == "add") {
		$('#mod_broker').hide();
		$('#add_broker').show();
	} else { 
    	Dajaxice.brokers.getBroker(showBroker, {'pk': value}, {'error_callback': custom_error}); 		
    }       
    
}

function showBroker(data) {
	$('#mod_broker').hide();
	$('#add_broker').hide();
	if(data.success == "true") {
		$('#mod_broker').show();
		$('#mod_pk').val(data.pk);
		$('#mod_name').val(data.name);
		$('#mod_commission').val(data.commission.toFixed(2));
	} else {
		html = "";
		html += data.message;
		$('#message').append(html);
	}
}

function modifyBroker() {
	
	Dajaxice.brokers.modifyBroker(showBroker, {'pk': value}, {'error_callback': custom_error});
}


function validate_required(field) {
	with (field) {
		if (value == null || value == ""){
			return false;
		} else {
			return true;
		}
	}
}

function validate_add(thisform) {
	$("#message").html("");
	with (thisform) {
		if (validate_required(add_name) == false) {
			$("#message").html("You must enter a name.");
			add_name.focus();
			return false;
		} else {
			$("#message").html("");
		}
		if (validate_required(add_commission) == false) {
			$("#message").html("You must enter the commission.");
			add_commission.focus();
			return false;
		} else {
			$("#message").html("");
		}
	}
	return true
}

function confirm_delete() {
	var result = confirm("Delete This Broker?")
  	return result;
}

