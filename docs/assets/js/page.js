let docs = {
	"event": {
		"is_func": false,
		"data": "class Event",
		"desc": "Основной объект (класс), который приходит к вам в модули",
		"members":{
			"etype": "тип эвента",
			"text": "полученное сообщение",
			"peer_id": "id чата, откуда получено сообщение",
			"userid": "id человека, который вызвал данный event",
			"splited": "массив слов, который составлен из сообщения пользователя в нижнем регистре",
			"args": "строка с сообщением пользователя",
			"message_id": "id сообщения",
			"bot": "класс данного бота (для подробностей см. bot)"
		}
	},
	"event.message_send()": {
		"is_func": true,
		"data": "event.message_send(message: string, peer_id: int = None, **params)",
		"desc": "отправляет сообщение",
		"args": {
			"message": "текст сообщения <span class=\"required\">*</span>",
			"peer_id": "id чата, куда будет отправлено сообщение",
			"params": "<a href = \"https://vk.com/dev/messages.send\"> допонительные параметры </a>"
		},
		"return": "Ответ от Vk API в формате JSON"
	},
	"event.bot": {
		"is_func": false,
		"data": "class Bot",
		"desc": "класс бота, который получил event",
		"members":{
			"token": "токен бота",
			"api_version": "версия api (если не задана, то используется «5.101»)",
			"names": "массив имен бота",
			"bot_id": "id бота из конфига",
			"main": "приоритет выполнения команд",
			"id": "id бота вк",
			"poll": "longpool Бота",
			"active": "статус активности бота (True/False)"
		}
	}
}

let hide_show_btn = document.getElementById("hide_btn")
let left = document.getElementById("left")
let right = document.getElementById("right")

function create_li(ul, name) {
	let li = document.createElement('li');
	ul.appendChild(li);
	li.innerHTML="<p>" + name + "</p>";
}

ul = document.getElementById("menu")
let params = Object.keys(docs)
for (let i=0; i<params.length; i++){
	create_li(ul, params[i])
}


function SearchAlgoritm() {
    let filter, ul, li, a, i;
	let input = document.getElementById("search");
		let eng = change_find(input.value)
		if (input.value !== eng){
			input.value = eng
		}
	//console.log(input.value);
    filter = input.value.toUpperCase();
    ul = document.getElementById("menu");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i];
        if (a["textContent"].toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function ChangeRight(li, hide_left = true){
	let methods = []
	if (hide_left) {
		if (window.innerWidth <= 700){
			hide_show_btn.id = 'show_btn';
			hide_show_btn.innerHTML = '>';
			right.classList.remove('hide');
			left.classList.remove('show');
			left.classList.add('hide');
		}
	}
	let doc = docs[li];
	let res = "<h1 class = \"chosen\">" + li + "</h1>\n";
	if (doc["is_func"]){
		res += "<pre style=\"margin-left:20px;\"><code data-language=\"python\">" + doc["data"] + "</pre></code>\n";
		res += "<h2>Описание:\n</h2>"
		res += "<p style=\"margin-left:20px;\">" + doc["desc"] +"\n</p>"
		let params = Object.keys(doc["args"])
		if (params.length !== 0){
			res += "<h2>Параметры:\n</h2>";
			//console.log(doc["args"])
			for (let i=0; i<params.length; i++){
				let arg = params[i]
				res += "<p style=\"margin-left:20px;\"><span style=\"color: green;\">" + arg + "</span>: " + doc["args"][arg] + "\n</p>";
			}
		}
		res += "<h2>Возращает:\n</h2>";
		res += "<p style=\"margin-left:20px;\">" + doc["return"] +"\n</p>"
	}else{
		res += "<pre style=\"margin-left:20px;\"><code data-language=\"python\">" + doc["data"] + "</pre></code>\n";
		res += "<h2>Описание:\n</h2>"
		res += "<p style=\"margin-left:20px;\">" + doc["desc"] +"\n</p>"
		let members = Object.keys(doc["members"])
		if (members.length !== 0){
			res += "<h2>Переменные:\n</h2>"
			//console.log(doc["args"])
			for (let i=0; i<members.length; i++){
				let member = members[i]
				res += "<p style=\"margin-left:20px;\"><span style=\"color: green;\">" + member + "</span>: " + doc["members"][member] + "\n</p>";
			}
		}
		let re_str = "(^" + li + ".)+\\\w+\\\(\\\)"
		let re = new RegExp(re_str)
		let docs_methods = Object.keys(docs)
		for (let i=0; i<docs_methods.length; i++){
			if (re.test(docs_methods[i])){
				methods.push(docs_methods[i])
			}
		}
		if (methods.length !== 0){
			res += "<h2>Методы:\n</h2>"
			for (i=0; i<methods.length; i++){
				res += "<p><span class = \"method\" style=\"margin-left:20px;\">" + methods[i] + "</span>: " + docs[methods[i]]["desc"] + "\n</p>";
			}
		}
	}
	res += "<br><br><span class=\"required\">*</span> - обязательный параметр!"
	res += "<div class = \"padding\"></div>"
	right.innerHTML = res;

	if (methods.length !== 0){
		let methods_in_html = document.getElementsByClassName("method")
		for(let i=0; i<methods_in_html.length; i++){
			methods_in_html[i].addEventListener('click', event => {
				if (event["type"] === "click"){
					Set_color(event.target["textContent"])
					ChangeRight(event.target["textContent"])
				}
			})
		}
	}


	Rainbow.color();
	//console.log()
}

function Set_color(event){
	let li = document.getElementById("menu").getElementsByTagName("li");
	for (let i = 0; i < li.length; i++) {
		if (li[i]["textContent"] !== event)
			li[i].innerHTML = "<p>" + li[i]["textContent"] + "</p>"
		else
			li[i].innerHTML = "<p class=\"chosen_li\">" + event + "</p>"
	}
}


document.getElementById("search").addEventListener('input', SearchAlgoritm);
li = document.getElementById("menu").getElementsByTagName("li");
for (let i = 0; i < li.length; i++) {
	li[i].addEventListener('click', event => {
		if (event["type"] === "click"){
			Set_color(event.target["textContent"])
			ChangeRight(event.target["textContent"])
		}
	})
}

hide_show_btn.addEventListener("click", () => {
		if (hide_show_btn.id === "hide_btn"){
			hide_show_btn.id = 'show_btn';
			hide_show_btn.innerHTML = '>';
			left.classList.remove('show');
			left.classList.add('hide');
	}else{
		hide_show_btn.id = 'hide_btn';
		hide_show_btn.innerHTML = '<';
		left.classList.remove('hide');
		left.classList.add('show');
	}
	right.classList.toggle('hide');
})



function change_find(str)
{
	const replace = ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ",
		"ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э",
		"я", "ч", "с", "м", "и", "т", "ь", "б", "ю"];
	const search = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]",
		"a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'",
		"z", "x", "c", "v", "b", "n", "m", ",", "."];

	for (let i = 0; i < replace.length; i++) {
		let reg = new RegExp(replace[i], 'mig');
		str = str.replace(reg, function (a) {
        return a === a.toLowerCase() ? search[i] : search[i].toUpperCase();
    })
}
  return str
}



Set_color("event")
ChangeRight("event", false)
