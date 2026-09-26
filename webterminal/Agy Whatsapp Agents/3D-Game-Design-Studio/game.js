/*
isSystemOnline = true;

if (isSystemOnline) {
  console.log("Proceed")
}



let oxygenLevel = 45;

if (oxygenLevel > 50) {
  console.log("Proceed")
}
else {
  console.log("Plz put in Oxygen Mask")
}

//level 3

let starDistance = 5; // Light Year

if (starDistance < 2) {
  console.log("Its a neighbour Star ")
}
else if (starDistance >= 2 && starDistance <= 10) {
  console.log("It has long distant ")
}
else {
  console.log("Long distant")
}



//level 4

let fuel = 80;
let engineHealth = 90;

if (fuel < 70 && engineHealth <80) {
  console.log("not ok")
}
else {
  console.log("ok")
}




// level 5
let a = 250;
let status = (a < 100)?  "So cold" : "No cold";

console.log(status)






let plannetType = "terristeriaal"
let hasWater = true;

if (plannetType === "terristerial") {
  if (hasWater) {
    console.log("Possible")
  }
  else {
    console.log("Not Possible")
  }}

else {
   console.log("gas ")
  
}



let a = 'Mars'
switch (a){
  case 'Mars':
    console.log("hi 1");
    break;
    
  case 'Moon' :
    console.log("hi 2");
    break;
    
  default:
  console.log("ok");
}


let spaceshipName = 'NameTest'; // খালি স্ট্রিং হলো Falsy

if (spaceshipName) {
    console.log(`জাহাজের নাম: ${spaceshipName}`);
} else {
    console.log("জাহাজের কোনো নাম নেই।");
}


আহা! এখন আপনার আসল confusion টা বুঝলাম! চলুন clear করি:

## স্বাভাবিক if statement:

সাধারণত আমরা এভাবে লিখি:

```javascript
if (spaceshipName === "") {  // পরিষ্কার comparison
    console.log("জাহাজের কোনো নাম নেই।");
} else {
    console.log(`জাহাজের নাম: ${spaceshipName}`);
}
```

বা 

```javascript
if (spaceshipName !== "") {  // not equal চেক
    console.log(`জাহাজের নাম: ${spaceshipName}`);
} else {
    console.log("জাহাজের কোনো নাম নেই।");
}
```

## কিন্তু `if (spaceshipName)` কী করে?

এটা একটা **shorthand/shortcut** পদ্ধতি। JavaScript এখানে automatically চেক করে:

```javascript
if (spaceshipName) 
// এর মানে হলো ↓
if (spaceshipName !== "" && spaceshipName !== null && spaceshipName !== undefined)
```

JavaScript নিজে থেকেই variable টাকে **boolean এ convert** করে ফেলে:
- যদি ফাঁকা (`""`) → `false`
- যদি কিছু থাকে (`"Apollo"`) → `true`

## দুটো পদ্ধতির তুলনা:

**পদ্ধতি ১ (স্পষ্ট):**
```javascript
if (spaceshipName !== "") {
    console.log("নাম আছে");
}
```

**পদ্ধতি ২ (shorthand):**
```javascript
if (spaceshipName) {
    console.log("নাম আছে");
}
```

দুটোই একই কাজ করে! তবে দ্বিতীয়টা আরো সংক্ষিপ্ত এবং experienced developers রা বেশি ব্যবহার করে।

আপনার বলা ঠিক আছে - **if এর ভিতরে true/false check হয়**, কিন্তু JavaScript সেই variable কে automatically true/false এ convert করে নেয়!



JavaScript
let isAdmin = true;
isAdmin && console.log("অ্যাডমিন প্যানেল সক্রিয়।");

let userPreference = null;
let theme = userPreference || "Dark Mode";
console.log(theme);


আমি আপনাকে এই JavaScript কোডটা ব্যাখ্যা করে দিচ্ছি:

**প্রথম অংশ - Logical AND (&&) অপারেটর:**

```javascript
let isAdmin = true;
isAdmin && console.log("অ্যাডমিন প্যানেল সক্রিয়।");
```

এখানে `&&` (AND) অপারেটর একটা শর্টহ্যান্ড হিসেবে কাজ করছে। এটা বলছে:
- যদি `isAdmin` true হয়, তাহলে ডান দিকের কোড রান করো (console.log)
- যদি `isAdmin` false হতো, তাহলে কিছুই রান হতো না

যেহেতু `isAdmin = true`, তাই কনসোলে প্রিন্ট হবে: **"অ্যাডমিন প্যানেল সক্রিয়।"**

**দ্বিতীয় অংশ - Logical OR (||) অপারেটর:**

```javascript
let userPreference = null;
let theme = userPreference || "Dark Mode";
console.log(theme);
```

এখানে `||` (OR) অপারেটর ডিফল্ট ভ্যালু সেট করতে ব্যবহার হচ্ছে:
- যদি `userPreference` এর মান truthy হয় (যেমন কোনো string, number ইত্যাদি), তাহলে সেটাই `theme` এ assign হবে
- যদি `userPreference` falsy হয় (null, undefined, false, 0, "" ইত্যাদি), তাহলে ডান দিকের ভ্যালু অর্থাৎ "Dark Mode" assign হবে

যেহেতু `userPreference = null` (যা falsy), তাই `theme = "Dark Mode"` হবে এবং কনসোলে প্রিন্ট হবে: **"Dark Mode"**

এগুলো খুবই কমন প্যাটার্ন JavaScript এ conditional logic এবং default values সেট করার জন্য।




let isAdmin = true ;
isAdmin && console.log("ekhane && directly if statement er poriborte byabhrito hoise")


let userPreference = null ;
let theme = userPreference || "Dark Mode" ;
console.log(theme);





let userAdmin = "Rahim" ;
userAdmin && console.log("userAdmin var worked")

let userPreference = "Okay Theme";
let theme = userPreference || "Dark Theme"

console.log(theme)

চমৎকার! আপনি পুরোপুরি সঠিক লিখেছেন! 👍

চলুন দেখি কী output আসবে:

## আপনার Code:

```javascript
let userAdmin = "Rahim";
userAdmin && console.log("userAdmin var worked")
```
**Output:** `"userAdmin var worked"` 
(কারণ `"Rahim"` হলো truthy, তাই `&&` এর ডান পাশ execute হবে)

```javascript
let userPreference = "Okay Theme";
let theme = userPreference || "Dark Theme"

console.log(theme)
```
**Output:** `"Okay Theme"`
(কারণ `"Okay Theme"` হলো truthy, তাই `||` বাম পাশের value টাই নিবে। `"Dark Theme"` তে যাবেই না)

## সম্পূর্ণ Console Output:

```
userAdmin var worked
Okay Theme
```

---

## বুঝার জন্য:

- `&&` বলে: "বাম পাশ truthy হলে ডান পাশ execute করো"
- `||` বলে: "বাম পাশ truthy হলে সেটাই নাও, নইলে ডান পাশ নাও"

আপনি perfect বুঝেছেন! 🎉 

এখন যদি `userPreference = null` বা `""` দিতেন, তাহলে `theme = "Dark Theme"` হতো। Try করে দেখতে পারেন!





let something = ""; //falsy value not true tai execute hobe naa

if (something) {
  console.log("Hi, value is truethy")
} 
else{"no high, value is not truthy"}


let userSomething = null;
if (userSomething){
  console.log("not Null value so print it")
}
else{
  console.log("eta null value")
}


*/


// Starting From book The Javascript The Programming Language









/*





let hello = "Hellow World";

let message = hello;

console.log(message)


const COLOR_RED = "#F00";
console.log(COLOR_RED)


console.log(1/0)



let isGreater = 4>1;

console.log(isGreater)




console.log(typeof 10n)


let dataType_1 = Symbol("id")
console.log(dataType_1)
console.log(typeof Math)
console.log(typeof alert)




let value = true;
console.log(typeof value); // boolean

value = String(value); // now value is a string "true"

console.log(typeof value); // string




console.log("6"/"2"); //string converted to value automatically

*/

//console.log(1+"1")


//"" + 1 + 0 //0+10 concatenate 
//"" - 1 + 0 // 0-1+0
//true + false// 1+0
//6 / "3" // 6/3
//"2" * "3" // 2*3
//4 + 5 + "px" // "9px"
//"$" + 4 + 5 // "$4" + 5
//"4" - 2 //4-2
//"4px" - 2 // Nan
//7 / 0 //Infinite 
//" -9 " + 5 // "_9" + 5 ➤ "-95"
//" -9 "  - 5  // -9-5
//null + 1 // 0+1
//undefined + 1 // Nan

//" \t \n" - 2 
// ""-2 ➤ -2

/*
/*
ভালো প্রশ্ন 👍
খুব শর্ট + পরিষ্কার উত্তর দিচ্ছি।


---

কেন \t আর \n কে whitespace ধরা হয়?

কারণ এগুলো দেখা যায় না এমন ফাঁকা জায়গা (space) তৈরি করে।

Symbol	মানে

\t	Tab → বড় ফাঁকা জায়গা
\n	New line → নতুন লাইনে নামা
' '	Space → সাধারণ ফাঁকা জায়গা


👉 এরা কেউই কোনো অক্ষর বা সংখ্যা না, শুধু জায়গা নেয় — তাই এদের বলে whitespace।


---

JavaScript কেন whitespace ignore করে (number বানানোর সময়)?

JS যখন string → number বানায়:

1. শুরু ও শেষের whitespace কেটে ফেলে


2. যদি কিছু না থাকে → 0



Number(" \t \n") // 0

তাই:

" \t \n" - 2
→ 0 - 2
→ -2


---

এক লাইনে মনে রাখো 🧠

👉 Space, tab (\t), newline (\n) = whitespace = ফাঁকা জায়গা

এটাই পুরো রহস্য 😊









var userInput = prompt("enter a letter :");

userInput = userInput.toLowerCase();

if (userInput.length != 1 && isNaN(userInput)) {
  console.log("Invalid Input")
}

switch (userInput) {
  case 'a':
  case 'e':
  case 'i':
  case 'o':
  case 'u':
  console.log("Vowel")
    break;
  
  default:
    console.log("Consonant")
}


*/

//From Anisul video Task
/*
sum =0;

for (i=1; i<=100; i++){
 // console.log(i)
  if(i%3==0 && i%5 ==0)
  sum = sum + i
  
  
}

console.log(sum);





i=1;
sum =0;

while (i<=100) {
 // console.log(i)
  if(i%3==0 && i%5 ==0)
  sum = sum + i
  i++
}

console.log(sum);

*/
/*

i=1;
sum =0;

while (i<=100) {
 // console.log(i)
  if(i%3==0 && i%5 ==0)
// console.log(i)  
  if (i == 50) {
    break
  }
  sum = sum + i
  //console.log(i)
  i=i+1
  //console.log(i)
}

console.log(sum);


*/

/*

let i = 0;
sum = 0;

while (i<100) {
  if (i == 10) {
    break
  }
  console.log(i)
  i++
}
*/

/*

let i = 1;
//sum = 0;

while (i<100) {
  i++
  if (i%2 == 0) {
    continue;
  }
  console.log(i)
  i++
}
*/


// i++ আগেই ব্যবহার করা হয়েছে কারণ এইটা লেখার সময় মিসিং হওয়ার ঝুকি আছে
// i++ অর্থাৎ i  না বাড়ালে লুপ i=1 নিয়েই পরে থাকবে।
// আর শেষে i++ দেওয়ার কারণ, বিজোড় সংখ্যা।
/*
প্রথম i++ (জোড় সংখ্যার ক্ষেত্রে):
যখন i এর মান ০, তখন শর্ত অনুযায়ী সেটি জোড়। এখন যদি আমরা i এর মান না বাড়িয়েই continue দিই, তবে প্রোগ্রাম আবার ০ নিয়ে লুপ শুরু করবে। তাই continue বলার ঠিক আগে আমরা i++ করে মান ১ করে দিচ্ছি। এতে করে লুপটি যখন উপরে ফিরে যায়, তখন সে নতুন মান ১ নিয়ে কাজ শুরু করতে পারে।
​২. দ্বিতীয় i++ (বিজোড় সংখ্যার ক্ষেত্রে):
যখন i এর মান ১ (বিজোড়), তখন সেটি if শর্তের ভেতরে ঢোকে না। ফলে প্রোগ্রামটি নিচের দিকে নামে এবং console.log(i) কাজ করে। এখন যদি এখানে i++ না থাকে, তবে লুপটি যখন আবার উপরে যাবে, সে তখনো ১ কেই খুঁজে পাবে। ফলে সে বারবার ১ প্রিন্ট করতেই থাকবে।
*/

/*
let i = 1;
//sum = 0;

while (i < 100) {
  i++
  if (i % 2 != 0) {
    continue;
  }
  console.log(i)
  i++
  if (i==11) { //ekhane 10 dile 100 porjonto cholbe cause eti mithya
    break
  }
}


*/

/*
let i = 1;
//sum = 0;

while (i < 100) {
  i++
  if (i % 2 != 0) {
    continue;
  }
  console.log(i)
  i++
  if (i < 15) {
    break;
    //i++
  }
}


*/

/*

let i = 1;
//sum = 0;

while (i < 100) {
  i++
  if (i%2 == 0 && i%4 == 0) {
    console.log("FizzBuzz")
  }
  else if (i%2 == 0) {
    console.log("Fizz")
  }
  else if (i%4 == 0) {
    console.log("Buzz")
  }
  else {
    console.log(i)
 
  }
}



*/
/*


let i = 1;
//sum = 0;

while (i < 100) {
  i++
  if (i % 3 == 0 && i % 7 == 0) {
    console.log("FizzBuzz")
  }
  else if (i % 3 == 0) {
    console.log("Fizz")
  }
  else if (i % 7 == 0) {
    console.log("Buzz")
  }
  else {
    console.log(i)
    
  }
}

*/

/*

(function fname(param) {
  console.log("immediately invoked")
})();


*/


/*

(function fname(param) {
  console.log(param)
})("Hello");

*/

/*

let funcExpression = function fname(param) {
  console.log(param)
};

funcExpression("Hi Vai")

*/


//result = prompt(title, [default]);

// procademy


//functiom checkEligibility(age) 



























//Interactive Cares, Function By Setu vai




/*
function hello (hi) {
  //console.log("Hellow" + hi)
  console.log(arguments)
}

//hello()

let arr_1 = ['w', 1, 3, 6, 8]

for (let i = 0; i<arr_1.length; i++) {
  if (arr_1 != '') {
    hello('name', 'vai')
  }
}



*/











//Previous Classes
/*
let num = 10;
num += num++ //num = num+10 //plus will not execute
console.log(num);
*/

//

/*

let num = 10;
let hi = num++ //num er value update kore num er modhyei rakho.....
console.log(num)
console.log(hi)

//
*/


/*

use std::pin::Pin;
use std::marker::PhantomPinned;

struct ComplexNode {
    value: String,
    self_ptr: *const String,
    _pin: PhantomPinned,
}

impl ComplexNode {
    fn new(val: &str) -> Self {
        ComplexNode {
            value: String::from(val),
            self_ptr: std::ptr::null(),
            _pin: PhantomPinned,
        }
    }

    fn init(self: Pin<&mut Self>) {
        unsafe {
            let mut_self = self.get_unchecked_mut();
            mut_self.self_ptr = &mut_self.value;
        }
    }

    fn value_ptr(self: Pin<&Self>) -> *const String {
        self.self_ptr
    }
}

fn main() {
    let mut node = Box::pin(ComplexNode::new("Future Context 2026"));
    
    node.as_mut().init();

    println!("Value address: {:p}", &node.value);
    println!("Stored pointer: {:p}", node.as_ref().value_ptr());
}





//let arr = [1,2]

let arr1 = []

let newArr = arr1;

arr1[0] =5;
arr1[arr1.length] = 7

console.log(newArr)




let arr = ['Liton', 'Sabbir', 'Somyo']
let lordArr = []

for (let i =0; i<arr.length; i++) {
  //lordArr.push(`Lord ${arr[i]}`)}
  //console.log(lordArr)}
  
  lordArr[i] = `Lord ${arr[i]}`}
  
console.log(lordArr)
  
  



let nums =[1,2,3,4,5,6,8,8,9,10]
let newNums = []

for (let i =0; i<10; i++) {
  if (nums[i] %2 ==0) 
  newNums.push(nums[i])
}
nums.push(newNums)
console.log(nums)






function calc(num1, operation, num2) {
switch (operation) {
  case '+':
    return num1 + num2;
    
  case '-':
    return num1 - num2;
   
  case '*':
    return num1 * num2;
    
  case '/':
    return num1 / num2;
    
  default:
    console.log("Enter valid Ooeration")
}}

console.log(calc(1,'+',3))


//

function func1() {
  // Tab to edit
  console.log("This is Func1")
}

function func2(param) {
  param()
}

func2(func1)







let sayHello = () => 2
console.log(sayHello())






function adder (num1, num2,...arr) {
  return num1+num2 + arr
}

console.log(adder(1,2,3,4,5))





let arr = [1,2,4,7,9]
let result = 0;
for (i = 0; i<arr.length; i++) {
  result = result + arr[i]
}
console.log(result)




function adder (...arr) {
  let result = 0;
  for (let i=0; i<arr.length; i++) {
    result = result + arr[i]
    
  }
  return result
  
}

let myNums = [3,4,5,6,7,8]

console.log(adder(...myNums))





function adder (...arr) {
  let result = 0;
  
  for (let i=0; i<arr.length; i++) {
    result = result + arr[i]
  }
  return result;
  
}

let myNums = [5,70, 8, 0, 5, 90]

console.log(adder(...myNums))





let person = {
  name : 'Iroan',
  age: 1.9,
  addr : 'Dhaka',
  sayHello: () => console.log("Hellow")
  
}


for (let el in person) {
  if (typeof person[el] === 'function') {
    person[el]()
  } else {
    console.log(person[el]) //el is already giving string like 'Iroan'
  
}

}





//let sayHello = () => console.log("Hellow")

//console.log(sayHello())


//Factory Function

function createPhone(brand, model, price){ return {
  brand : brand,
  model: model,
  price: price,
  
}
}

phone1= createPhone("Samsung", "S24", 200000)

console.log(phone1)





function CreatePhone(phoneName, phoneModel) {
  this.phone = phoneName;
  this.model = phoneModel;
  this.sayHello = () => {
    console.log("sayHello")
  }
}

let phone1 = new CreatePhone("Samsumg", "s24")

console.log(phone1)




let interest = ["Python", "Js", "PHP"]

interest.forEach(function (el, vai1, vai3) {
  console.log(vai3)
  // Tab to edit
})

interest





let players = ["Tamim", "Jaker Ali"]

let lordName = [];

for (let i = 0; i<players.length; i++) {
  lordName.push('Lord ' + players[i])
}

console.log(lordName)




let players = ["Tamim", "Jaker Ali"]
players.map(function (v1, v2, v3) {
  console.log(v2)
})





let players = ["Tamim", "Jaker Ali"]
players.map(function (v1, v2, v3) {
  return 6
})

console.log(players)


let arrName = new Array('Rahim', 'Karim', 'Jabbar')

console.log(arrName)




let arrName = ['Rahim', 'Karim', 'Jabbar',  'Elita']


arrName[5] = 'Vai';

console.log(arrName['length'])



let arrName = ['Rahim', 'Karim', 'Jabbar',  'Elita']


for (let i =0; i<arrName.length; i++) {
  console.log('Name: ' + i +  ' ' + arrName[i])
}






let arrName = ['Rahim', 'Karim', 'Jabbar',  'Elita']


let newSpliceArr = arrName.splice(2);

console.log(arrName)

console.log(newSpliceArr)





let rahim = {
  fullName : 'Rahim Miya',
  age : 21,
  add : 'Dhaka',
  otherNames : ['Mohammad', 'Abdur', 'Rahim']
  
}

rahim.zipCode = 3357
rahim.job = 'Store Keeper'
rahim.welcomeMsg = function () {
  return console.log("New Function Added")
}

console.log(rahim.fullName)

console.log(rahim.welcomeMsg())
console.log(rahim.otherNames[1])




function square(x) {
  console.log(`Square of ${x} : ${x*x}`)
}
const y = square
//y(6)

function higherOrderFunc (num, callB) {
  callB(num) //callB kintu csllB na, eta square function ke call kora holo
}
higherOrderFunc(6, y)

//square function asole kothao call hoyni untill callB was there, so, callB tai muloto square function



let cricketerName = ['Liton', 'Mithun', 'Jaker Ali', 'Mithun']

let lordName = cricketerName.map((el) => 'Lord' + el);

console.log(lordName);




let nums = [1,2,3,4,5,6,7,8]
let newNums = nums.filter((elements) => {
  return elements % 2 === 0;
});
console.log(newNums)


let nums = [1,2,3,4,5,6,7,8]
nums.map(arr) {
  console.log(arr);
})





let arr = new Array();

for (let i =0; i<5; i++) {
  arr[i] = parseInt(prompt("Enter a number: "))};
console.log(arr)



console.log("arr")
console.log("arr")
console.log("arr")


let sum = 0;

for (let i =0; i<5; i++) {
  sum = sum + arr[i]
}

console.log(sum)







let nums = [1,2,3,4,5,6,7,8]

nums.splice(2,1, 66)
nums.sort(function(a,b) {
  return a-b;
});

console.log(nums)



let arr = ["Rahim", "Karim", " Jodu", "Modu", " Kodu"]

let numbers = [100, 1,66, 88, 99, 2]
function cricketScores(scores) {
  let max = numbers[0];
  for (let i =1; i<numbers.length; i++) {
  if (max < numbers[i]) {
    max = numbers[i]
  }
}
//console.log(max)
return max
}


let highestScore = cricketScores(numbers);

console.log(highestScore)





//let cricketerName = ["Rahim", "Karim", "Jodu", " Modu", "Kodu"]



function CricketerScore(arr2) {
  let maxScore = arr2[0]
  for (let i=1; i<arr2.length; i++) {
    //let maxScore = arr2[0]
    if (maxScore < arr2[i])
    maxScore = arr2[i]
}
  return maxScore;
}

let score = [1,100,200, 600, 4, 300]

let highestScore = CricketerScore(score)
console.log(highestScore)

*/

let primaryObj = {
  name:'Rahim Vai',
  age : 16,
  anotherObj : {
    name : 'Karim Vai',
    value : function() {
      console.log("My Name is " + this.name);
    }
  }
}

primaryObj.anotherObj.value.apply(primaryObj);

