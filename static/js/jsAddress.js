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
    var house_type = data.parentNode.getElementsByTagName("span")[0].className;
    var city = data.parentNode.getElementsByTagName("span")[1].className;
    var area = data.parentNode.getElementsByTagName("span")[2].className;
    var state = data.parentNode.getElementsByTagName("span")[3];
    const finalUrl = `/result?house_type=${house_type}&city=${city}&area=${area}`;
    if (state.className == "3"){
        window.location.href = finalUrl;
    }
    else {
        alert(`${state.textContent} 抓取完成即可查看!`);
    }
};

function DeleteBtn(data) {
    var house_type = data.parentNode.getElementsByTagName("span")[0].className;
    var city = data.parentNode.getElementsByTagName("span")[1].className;
    var area = data.parentNode.getElementsByTagName("span")[2].className;
    var state = data.parentNode.getElementsByTagName("span")[3];
    const finalUrl = `/delete?house_type=${house_type}&city=${city}&area=${area}`;
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

function xiaoqu_detail(xiaoqu_data){
    let get_url = `/get_xiaoqu_detail?xiaoqu_name=${xiaoqu_data}`;
    window.location.href = get_url;
};

function xiaoqu(windows) {
    var tables = windows.getElementsByTagName('table');
    if (tables) {
        let table_tr = tables[0];
        for (let index = 1; index < table_tr.rows.length; index++) {
            for (let i = 0; i < table_tr.rows[index].children.length; i++) {
                if (i === 4) {
                    table_tr.rows[index].children[i].onclick = function(){xiaoqu_detail(table_tr.rows[index].children[i].textContent);};
                    table_tr.rows[index].children[i].style.cursor="pointer";
                }
            }
        }
    }
};

//传入坐标，然后跳转到该位置
function showMap(x, y) { 
    var map = new BMap.Map("mymap");
    map.centerAndZoom(new BMap.Point(x, y), 15); //坐标，放大倍数
    //显示左上角的辅助栏
    map.addControl(new BMap.NavigationControl());
    //创建小红点
    var marker = new BMap.Marker(new BMap.Point(x, y));
    map.addOverlay(marker);
    map.enableScrollWheelZoom(true); // 开启鼠标滚轮缩放
    //穿件创建小红点上的提示框
    // var infoWindow = new BMap.InfoWindow("<p>名字:风玡</p><p>phone:12345678911</p>");
    // marker.addEventListener("click", function(){
    //     this.openInfoWindow(infoWindow);
    // })
};

function xiaoqu_map(xiaoqu) {
    var lat, lng;
    var tables = xiaoqu.getElementsByTagName('table');
    if (tables) {
        let table_tr = tables[0].children[0].children;
        for (let index = 0; index < table_tr[1].children.length; index++) {
            if (index === 9) {
                lat = table_tr[1].children[index].textContent;
                table_tr[0].children[index].style.display = 'none';
                table_tr[1].children[index].style.display = 'none';
            }
            if (index === 10) {
                lng = table_tr[1].children[index].textContent;
                table_tr[0].children[index].style.display = 'none';
                table_tr[1].children[index].style.display = 'none';
            }
        }
        $(function(){
            showMap(lng,lat); //初始坐标
        })
    }
};
