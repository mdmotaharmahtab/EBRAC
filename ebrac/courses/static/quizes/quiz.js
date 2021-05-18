console.log('hello world quiz')
const url = window.location.href
const quizBox = document.getElementById("quiz-box")
const scoreBox = document.getElementById("score-box")
const resultBox = document.getElementById("result-box")
const countdownBox = document.getElementById("countdown-box")
const quizForm = document.getElementById("quiz-form")
const csrf = document.getElementsByName("csrfmiddlewaretoken")
const quiz_time = parseFloat(countdownBox.getAttribute('data-time')) * 60

$.ajax({
    'type':'GET',
    'url' : `${url}data`,
    
    'success': function(response){
       
        const data = response.data
        //console.log(response.time)
        
        data.forEach(el => {
            for (const [question,answers] of Object.entries(el)){
                
                quizBox.innerHTML += `
                
                    <hr>
                    <div class="mb-2">
                    
                        <b>${question}</b>
                    </div>
                
                `
                answers.forEach(answer => {
                
                    quizBox.innerHTML += `
                        <div>
                            <input type="radio" class="ans" 
                            id="${question}-${answer}" name="${question}" value="${answer}">
                            <label for="${question}">${answer}</label>
                            
                        </div>
                    
                    `
                }) 
            }
        });
        
    },
    
    'error': function(error){
        console.log(error)
    }

})




const sendData = () =>{
    const elements = [...document.getElementsByClassName("ans")]
    const data = {}
    data['csrfmiddlewaretoken'] = csrf[0].value
    elements.forEach(el =>{
        if (el.checked){
            data[el.name] = el.value
            
        }
        else{
            if(!data[el.name]){
                data[el.name] = null
            
            }
        
        }
    })
    
    $.ajax({
    
        type : 'POST',
        url : `${url}save/`,
        data : data,
        success : function(response){
            // console.log(response)
            const results = response.results
            console.log(results)
            quizForm.classList.add('not-visible')
            countdownBox.classList.add('not-visible')
            scoreBox.innerHTML = `${response.passed ? 'Congrats! ' : 'Failed! '}Your result is ${response.score}%`
            
            
            results.forEach(res => {
                const resDiv = document.createElement("div")
                
                for (const [question,resp] of Object.entries(res)){
                    
                    resDiv.innerHTML += question
                    const cls = ['container','p-3','text-light','h3']
                    resDiv.classList.add(...cls)
                    
                    if(resp == "not answered"){
                        resDiv.innerHTML += "- Question not answered"
                        resDiv.classList.add('bg-danger')
                    }
                    else{
                        const answer = resp['answered']
                        const correct = resp['correct_answer']
                        
                        // console.log(answer,correct)
                        if (answer == correct){
                            
                            resDiv.classList.add('bg-success')
                            resDiv.innerHTML += `answered: ${answer}`
                        }
                        else{
                            resDiv.classList.add('bg-danger')
                            resDiv.innerHTML += `| correct answer: ${correct}`
                            resDiv.innerHTML += `| answered: ${answer}`
                            
                        
                        }
                    
                    }
                
                }
                
                resultBox.append(resDiv)
                
            })
        },
        error : function(error){
            console.log(error)
        }
    })
}

        
var sec = 0
const event = new Event('submit')
quizForm.addEventListener('submit', e=> {
    e.preventDefault()
    clearInterval(myCountDown)
    sendData()
                            
                    })              
const myCountDown = setInterval(()=>{
                    sec +=1
                    console.log(sec)
                    if (sec-quiz_time>=1){
                    clearInterval(myCountDown)
                    quizForm.dispatchEvent(event);
                    }
                    else{
                        //remaining_time = end_time-time_now
                        remaining_time = quiz_time-sec
                        h = Math.floor(remaining_time /3600)
                        m = Math.floor((remaining_time %3600)/60)
                        s = (remaining_time %3600)%60
                        countdownBox.innerHTML = h + 'hours ' + m+'minutes '+s+'seconds '
                       
                    }
                    
                },1000)

//quizForm.dispatchEvent(event);