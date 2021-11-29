package com.example.myapplication

import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.myapplication.databinding.ActivityMainBinding
import okhttp3.Response


class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    lateinit var bitmap: Bitmap
    lateinit var imgview: ImageView
    private val flaskposturl: String = "http://10.0.2.2:5000/predict"
//    lateinit var response_global: Response

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // https://www.youtube.com/watch?v=27kdAqDUpcE&ab_channel=ProgrammingFever
//        if (! Python.isStarted()) {
//            Python.start(AndroidPlatform(this));
//        }
//        var py: Python = Python.getInstance();
//        var pyo: PyObject = py.getModule("predict")//"hello")
//        Log.d("DEBUG", "Got the python module $pyo")

        imgview = findViewById(R.id.imageView)
        var tv:TextView = findViewById(R.id.textView)
        var select: Button = findViewById(R.id.button)
        select.setOnClickListener(View.OnClickListener {
            Log.d("DEBUG","UPLOAD WAS CLICKED")
            var intent: Intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(intent, 100)
            tv.setText("Click on Predict!")
        })

        var predict:Button = findViewById(R.id.button2)
        predict.setOnClickListener(View.OnClickListener {
            var imageString: String= APICalls.getImageString(bitmap)
            // FLASK https://medium.com/analytics-vidhya/how-to-make-client-android-application-with-flask-for-server-side-8b1d5c55446e
            Log.d("DEBUG", "CALLING PREDICT NOW")
            // https://stackoverflow.com/questions/30554702/cant-connect-to-flask-web-service-connection-refused
            // https://stackoverflow.com/questions/65467434/okhttp-unable-to-connect-to-a-localhost-endpoint-throws-connected-failed-econnr

            // wait for response https://stackoverflow.com/questions/57940361/kotlin-okhttp-api-call-promise
            APICalls.postRequest(imageString, this){
                var response:Response = it
                println("IN THE THEN")
                Log.d("DEBUG", "GOT THE RESPONSE IN MAINACTIVITY "+response.toString())
                val intent = Intent(this, RecipeListActivity::class.java)
                var responseBody = response.body!!.string()
                Log.i("ResponseBody", responseBody)
                intent.putExtra("similarity", responseBody)
                startActivity(intent)
            } // returns {"recipes":[{"title"...}, {"title"...}, ...]}
//            println("DOES THIS RUN BEFORE THE THEN BLOCK IS EXECUTED???") // Yes

//            // Runs model inference and gets result.
//            val obj: PyObject = pyo.callAttr("predict",imageString) // "helloworld"
//            Log.d("DEBUG", "THE OBJ IS $obj")
        })

        var goToRecipes:Button = findViewById(R.id.button3)
        goToRecipes.setOnClickListener(View.OnClickListener {
            APICalls.postRequest("goToRecipes", this){
                var response:Response = it
                Log.d("DEBUG", "GOT THE RESPONSE IN MAINACTIVITY "+response.toString())
                val intent = Intent(this, RecipeListActivity::class.java)
                var responseBody = response.body!!.string()
                Log.i("ResponseBody", responseBody)
                intent.putExtra("similarity", responseBody)
                startActivity(intent)
            }
//            val intent = Intent(this, RecipeListActivity::class.java)
//            startActivity(intent)
        })
    }


    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        imgview.setImageURI(data?.data)

        var uri: Uri?= data?.data
        bitmap = MediaStore.Images.Media.getBitmap(this.contentResolver, uri)

    }

    fun filterRecipeList(filterCategory: String){
        APICalls.postRequest(filterCategory, this){
                var response:Response = it
                println("IN THE THEN")
                Log.d("DEBUG", "GOT THE RESPONSE IN MAINACTIVITY "+response.toString())
                var responseBody = response.body!!.string()
                Log.i("ResponseBodyFilter", responseBody)
            }
    }



//    fun eggFreeFilterTapped(view: android.view.View) {
//        Log.i("eggfreefilter", "MainActivity")
//        var eggFreeFilter:Button = findViewById(R.id.eggFreeFilter)
//        eggFreeFilter.setOnClickListener(View.OnClickListener {
//            postRequest("eggFree", flaskposturl){
//                var response:Response = it
//                println("IN THE THEN")
//                Log.d("DEBUG", "GOT THE RESPONSE IN MAINACTIVITY "+response.toString())
////            val intent = Intent(this, RecipeListActivity::class.java)
//                var responseBody = response.body!!.string()
//                Log.i("ResponseBodyFilter", responseBody)
////            intent.putExtra("similarity", responseBody)
////            startActivity(intent)
//            }
//        })
//    }

}