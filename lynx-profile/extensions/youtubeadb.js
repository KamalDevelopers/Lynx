try {
    //Get every video element on the page and loop through them
    const videos = document.querySelectorAll("video");
    for(let i = 0; i < videos.length; i++){
        let video = videos[i];
        
        //Store the old pause function (this should be a native function to the <video> element)
        const   old_fn  =   video.pause;
        
        //Override the pause function with a custom one
        video.pause = function(){
            //Gather the JS execution stack
            const err = new Error();
            console.log(err.stack)
            //If the stack contains traces of not being user activated, block the pause request
            if(err.stack.toString().indexOf('$fa') >= 0){
                const is_paused =   video.paused;
                console.log("[Pause] Request blocked")
                //We still pause the video then play to keep the controls correct
                old_fn.call(this, ...arguments)
                if(is_paused == false){
                    video.play();
                }
            } else{
                console.log("[Pause] Request allowed")
                old_fn.call(this, ...arguments)
            }
        }
        
        //If it's already paused the video
        video.play();
    }
} catch(error){
    console.error(error)
}

const clear = (() => {
    const defined = v => v !== null && v !== undefined;
    const timeout = setInterval(() => {
        const ad = [...document.querySelectorAll('.ad-showing')][0];
        if (defined(ad)) {
            const video = document.querySelector('video');
            if (defined(video)) {
                video.currentTime = video.duration;
            }
        } 
    }, 500);
    return function() {
        clearTimeout(timeout);
    }
})();

document.addEventListener("keypress", function(event) {
    if (event.keyCode == 13) {
        clear(); 
    }
});
