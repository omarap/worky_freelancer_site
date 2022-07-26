
    $('#back').click(function goBack() {
		window.history.back();
	});


    function languages() {
        var languages = $("input[name='languages[]']:checked").map(function () {
            return this.value;
        }).get();

        if (languages.length == 0){
                $("input[type=submit]").attr("disabled", "disabled");
        }
        else{
            $("input[type=submit]").removeAttr("disabled");
        }
    }


function on() {
  document.getElementById("overlay").style.display = "block";
}

function off() {
  document.getElementById("overlay").style.display = "none";
}
