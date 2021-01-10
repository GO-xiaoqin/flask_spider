var addressInit = function (_cmbType, _cmbProvince, _cmbCity, _cmbArea, defaultType, defaultProvince, defaultCity, defaultArea) {
    var cmbType = document.getElementById(_cmbType);
    var cmbProvince = document.getElementById(_cmbProvince);
    var cmbCity = document.getElementById(_cmbCity);
    var cmbArea = document.getElementById(_cmbArea);

    function provinceList() {
        var city;
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
                    alert("没有获取到数据！");
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

    function cmbAddOption(cmb, str, obj, str_code) {
        var option = document.createElement("OPTION");
        cmb.options.add(option);
        option.innerText = str;
        option.value = str_code;
        option.obj = obj;
    }

    function changeCity() {
        cmbArea.options.length = 0;
        if (cmbCity.selectedIndex == -1) return;
        var item = cmbCity.options[cmbCity.selectedIndex].obj;
        for (var i = 0; i < item.area.length; i++) {
            cmbAddOption(cmbArea, item.area[i].area_name, null, item.area[i].area_code);
        }
        cmbSelect(cmbArea, defaultArea);
    }

    function changeProvince() {
        cmbCity.options.length = 0;
        cmbCity.onchange = null;
        if (cmbProvince.selectedIndex == -1) return;
        var item = cmbProvince.options[cmbProvince.selectedIndex].obj;
        for (var i = 0; i < item.city.length; i++) {
            cmbAddOption(cmbCity, item.city[i].city_name, item.city[i], item.city[i].city_code);
        }
        cmbSelect(cmbCity, defaultCity);
        changeCity();
        cmbCity.onchange = changeCity;
    }

    function changeType() {
        cmbProvince.options.length = 0;
        cmbProvince.onchange = null;
        if (cmbType.selectedIndex == -1) return;
        var item = cmbType.options[cmbType.selectedIndex].obj;
        console.log(item);
        // for (var i = 0; i < item.city.length; i++) {
        //     cmbAddOption(cmbProvince, item.city[i].city_name, item.city[i], item.city[i].city_code);
        // }
        for (var i = 0; i < item.length; i++) {
            cmbAddOption(cmbProvince, item[i].name, item[i], null);
        }
        cmbSelect(cmbProvince, defaultProvince);
        changeProvince();
        cmbProvince.onchange = changeProvince;
    }


    var city_data = provinceList();
    if (city_data != null){
        var data_type = [
            {'name': '小区房价', 'code': 'xiaoqu', 'houses_type': 1},
            {'name': '挂牌二手房',  'code': 'ershou', 'houses_type': 1},
            {'name': '新房',  'code': 'loupan', 'houses_type': 0},
        ];
        for (var i = 0; i < data_type.length; i++) {
            if (data_type[i].houses_type == 0){
                cmbAddOption(cmbType, data_type[i].name, city_data['result_fang'], data_type[i].code);
            };
            if (data_type[i].houses_type == 1){
                cmbAddOption(cmbType, data_type[i].name, city_data['result_ershou'], data_type[i].code);
            };
        }
        cmbSelect(cmbType, defaultType);
        changeType();
        cmbType.onchange = changeType;
    }
};

function btnAction(data) {
    var state = data.parentNode.getElementsByTagName("span")[2];
    var city = data.parentNode.getElementsByTagName("span")[0].className;
    var house_type = data.parentNode.getElementsByTagName("span")[1].className;
    const finalUrl = `/result?city=${city}&house_type=${house_type}`;
    if (state.className == "3"){
        window.location.href = finalUrl;
    }
    else {
        alert(`${state.textContent} 抓取完成即可查看!`);
    }
};

function DeleteBtn(data) {
    var state = data.parentNode.getElementsByTagName("span")[2];
    var city = data.parentNode.getElementsByTagName("span")[0].className;
    var house_type = data.parentNode.getElementsByTagName("span")[1].className;
    const finalUrl = `/delete?city=${city}&house_type=${house_type}`;
    if (state.className == "3"){
        window.location.href = finalUrl;
    }
    else {
        alert(`${state.textContent} 抓取完成即可删除!`);
    }
};

function login() {
    $.ajax({
    //几个参数需要注意一下
        type: "POST",//方法类型
        dataType: "json",//预期服务器返回的数据类型
        url: "/grab" ,//url
        data: $('#my-form').serialize(),
        success: function (result) {
            // console.log(result);//打印服务端返回的数据(调试用)
            if (result['status'] == "1") {
                window.location.href = "/"
            }
            if (result['status'] == "0"){
                alert(result['result']);
            }
        },
        error : function() {
            alert("异常！");
        }
    })
};
