fetch('https://jsonplaceholder.typicode.com/posts')
.then((res)=>{
    console.log(res.json())
})
.catch((error)=>{
    console.error(error);
    
})