var changed = false;
var canSave = false;
var ajaxError = false;
var enablePolling = true;
var okSettings = {};
var futzing = false;
var futzBrightness = 100;
var futzDisplay = "noon";

function setSaveMsg(msg, isError) {
   $("#save_msg").text(msg);

   var div = $("#save_msg_div");

   div.attr("class", isError ? "w3-container w3-cell w3-cell-middle w3-red" : "w3-container w3-cell w3-cell-middle w3-green");
   div.toggle(!!msg);
}

function doAjax(method, item, data, callback) {
   var params = {
      url: "/"+item,
      type: method,
      dataType: "json",
      success: function(result) {
	       if(ajaxError) {
				 ajaxError = false;
				 setSaveMsg("", false);
			 }	
          callback && callback(result);
      },
      error: function(jqXHR, textStatus, errorThrown) {
         ajaxError = true;
         setSaveMsg(
            jqXHR.status == 0 ? "The clock is not responding" : jqXHR.status.toString(), true);
         callback && callback(null);
     },
   }

   if(data != null) {
      params["contentType"] = "application/json";
      params["processData"] = false;
      params["data"] = JSON.stringify(data);
   }

   $.ajax(params);
}

function setValue(id, value) {
   $(id).val(value);
}

function changeSsid() {
   var value = $("#ssid").val();
   newSettings["ssid"] = value;

   displayError(
      value.length == 0,
      "ssid",
      "The SSID may not be blank.");

   enableSave();
}

function changePassword() {
   var value = $("#password").val();
   newSettings["password"] = value;

   displayError(
      value.length != 0 && value.length < 8,
      "password",
      "The Password must be at least 8 characters.");

   enableSave();
}

function changeLat() {
   checkInt("lat", "Latitude", -90, 90);
}

function changeLon() {
   checkInt("lon", "Longitude", -180, 180);
}

function changeMinLight() {
   checkRange("light", "Ambient Light", true, 0, 30000);
}

function changeMaxLight() {
   checkRange("light", "Ambient Light", false, 0, 30000);
}

function changeMinBrightness() {
   checkRange("brightness", "Brightness", true, 0, 100);
}

function changeMaxBrightness() {
   checkRange("brightness", "Brightness", false, 0, 100);
}

function changeSunrise() {
   newSettings["sunrise"] = $("#sunrise").val();
   enableSave();
}

function changeDisplayMode() {
	doAjax("POST", "mode", {display_mode: $("#display_mode").val()}, null);
}


function checkInt(id, name, min, max) {
   var value = Number($("#"+id).val());

   var ok = !displayError(
       isNaN(value) || value < min || value > max,
       id,
       name+" must be between "+min.toString()+" and "+max.toString()+".");

   if(ok) {
      newSettings[id] = value;
   }

   enableSave();
   return {value: value, ok: ok};
}

function checkRange(id, name, isMin, min, max) {
   var minId = "min_"+id;
   var maxId = "max_"+id;
   minResult = checkInt(minId, "Min "+name, min, max);
   maxResult = checkInt(maxId, "Max "+name, min, max);

   if(minResult.ok && maxResult.ok) {
      displayError(
         minResult.value > maxResult.value,
         isMin ? minId : maxId,
         "Min "+name+" may not be greater than Max "+name+".");

      enableSave();
   }
}

function showElement(id, show) {
   $(id).toggle(show);
}

function displayError(isBad, id, msg) {
   if(isBad) {
      $("#errmsg_"+id).text(msg);
   }

   showElement("#err_"+id, isBad);
   okSettings[id] = !isBad;
   return isBad;
}

function enableSave() {
   var newCanSave = true;

	if(!isHotspot) {
		for (const [key, value] of Object.entries(okSettings)) {
			if(!value) {
				newCanSave = false;
			}
		}

		if(newCanSave) {
			newCanSave = false;

			for (const [key, value] of Object.entries(curSettings)) {
				if(value != newSettings[key]) {
					newCanSave = true;
				}
			}
		}

		if(!canSave && newCanSave) {
			setSaveMsg("", false);
		}
	}

	$("#save").prop("disabled", !newCanSave);

   canSave = newCanSave;
}

function save() {
   doAjax(
      "POST", "save", newSettings,
      function(results) {
          if(!!results) {
             curSettings = Object.assign({}, newSettings);
				 isHotspot = false;
             enableSave();
             setSaveMsg(results.msg, !results.ok);

				 if(results.wifi_changed) {
					 enablePolling = false;
				 }
          }
      }
   );
}

function getState() {
	if(enablePolling) {
		doAjax(
			"GET", "state", null,
			function(results) {
				if(!!results) {
					$("#cur_ambient").text(results.cur_ambient.toString());
					$("#cur_brightness").text(results.cur_brightness.toString());
					$("#cur_angle").text(results.cur_angle.toString());
					setValue("#display_mode", results.display_mode);
					$("#sunrise_orientation").text(results.sunrise_orientation);

					var up;

					switch(results.cur_orientation) {
						case "face-up":
							up = "Face";
							break;
						case "back-up":
							up = "Back";
							break;
						case "right-up":
							up = "Right";
							break;
						case "bottom-up":
							up = "Bottom";
							break;
						case "left-up":
							up = "Left";
							break;
						default:
							up = "Top";
							break;
					}

					$("#cur_orientation").text(up);
				}

				setTimeout(getState, 1000);
			}
		);
	}
}

function ping() {
	if(futzing) {
		doAjax(
			"GET", "ping", null,
			function(results) {
				if(!!results && !results.ok) {
					hideFutz();
				}
		});

		if(futzing) {
			setTimeout(ping, 1000);
		}
	}
}

function showFutz() {
	futzing = true;

	$("#brightness").val(futzBrightness.toString());
	$("#futzdisplay").val(futzDisplay);

	futz();
	ping();

	document.getElementById('futz').style.display = "block";
}

function hideFutz() {
	futzing = false;
	doAjax("POST", "futz", {}, null);
	document.getElementById('futz').style.display='none';
}


function futz() {
	futzBrightness = Number($("#brightness").val());
	$("#brightness_value").text(futzBrightness.toString());
	futzDisplay = $("#futzdisplay").val();

	doAjax("POST", "futz", {brightness: futzBrightness, display: futzDisplay}, null);
}

function setMinBrightness() {
	$("#min_brightness").val(futzBrightness);
	newSettings["min_brightness"] = futzBrightness;

	if(futzBrightness > Number($("#max_brightness").val())) {
		$("#max_brightness").val(futzBrightness);
		newSettings["max_brightness"] = futzBrightness;
	}

	enableSave();
}

function setMaxBrightness() {
	$("#max_brightness").val(futzBrightness);
	newSettings["max_brightness"] = futzBrightness;

	if(futzBrightness < Number($("#min_brightness").val())) {
		$("#min_brightness").val(futzBrightness);
		newSettings["min_brightness"] = futzBrightness;
	}

	enableSave();
}


$(document).ready(
   function() {
      $("#version").text(version);
		$("#server_ip").text(serverIp);

      for (const [key, value] of Object.entries(curSettings)) {
         if(key != "password") {
            $("#"+key).val(Number.isFinite(value) ? value.toString() : value);
         }

         okSettings[key] = true;
      }

      enableSave();

      if(!!curSettings.ssid) {
         $("#password").attr("placeholder", "Leave this blank to retain the current password");
      }

      getState();
   }
);
