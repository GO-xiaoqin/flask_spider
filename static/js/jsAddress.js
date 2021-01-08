var addressInit = function (_cmbProvince, _cmbCity, _cmbArea, defaultProvince, defaultCity, defaultArea) {
    var cmbProvince = document.getElementById(_cmbProvince);
    var cmbCity = document.getElementById(_cmbCity);
    var cmbArea = document.getElementById(_cmbArea);

    function provinceList() {
        var city = {};
        $.ajax({
        //几个参数需要注意一下
            type: "GET",//方法类型
            dataType: "json",//预期服务器返回的数据类型
            url: "/get_city" ,//url
            async: false,
            // data: $('#my-form').serialize(),
            success: function (result) {
                // console.log(result);//打印服务端返回的数据(调试用)
                if (result['status'] === 1) {
                    city = result['result']
                }
                else {
                    alert("异常！");
                }
            },
            error : function() {
                alert("异常！");
            }
        });
        return city
    }

    function cmbSelect(cmb, str) {
        for (var i = 0; i < cmb.options.length; i++) {
            if (cmb.options[i].value == str) {
                cmb.selectedIndex = i;
                return;
            }
        }
    }

    function cmbAddOption(cmb, str, obj) {
        var option = document.createElement("OPTION");
        cmb.options.add(option);
        option.innerText = str;
        option.value = str;
        option.obj = obj;
    }

    function changeCity() {
        cmbArea.options.length = 0;
        if (cmbCity.selectedIndex == -1) return;
        var item = cmbCity.options[cmbCity.selectedIndex].obj;
        for (var i = 0; i < item.areaList.length; i++) {
            cmbAddOption(cmbArea, item.areaList[i], null);
        }
        cmbSelect(cmbArea, defaultArea);
    }

    function changeProvince() {
        cmbCity.options.length = 0;
        cmbCity.onchange = null;
        if (cmbProvince.selectedIndex == -1) return;
        var item = cmbProvince.options[cmbProvince.selectedIndex].obj;
        for (var i = 0; i < item.cityList.length; i++) {
            cmbAddOption(cmbCity, item.cityList[i].name, item.cityList[i]);
        }
        cmbSelect(cmbCity, defaultCity);
        changeCity();
        cmbCity.onchange = changeCity;
    }

    var city_data = provinceList();
    for (var i = 0; i < city_data['result_ershou'].length; i++) {
        cmbAddOption(cmbProvince, city_data['result_ershou'][i].name, city_data['result_ershou'][i]);
    }
    cmbSelect(cmbProvince, defaultProvince);
    // changeProvince();
    // cmbProvince.onchange = changeProvince;

    console.log(city_data)
};

