package com.example.myapplication

import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.util.Base64
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.beust.klaxon.JsonObject
// https://chaquo.com/chaquopy/doc/current/android.html#android-source
//import com.chaquo.python.PyObject
//import com.chaquo.python.Python
//import com.chaquo.python.android.AndroidPlatform
import com.example.myapplication.databinding.ActivityMainBinding
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.ByteArrayOutputStream
import okhttp3.Response
import okhttp3.OkHttpClient
import okhttp3.RequestBody
import java.io.IOException
import android.widget.Toast




class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    lateinit var bitmap: Bitmap
    lateinit var imgview: ImageView

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
            val imageString: String= getImageString(bitmap)

            Log.d("DEBUG", "CALLING PREDICT NOW")
            // TODO: API CALL TO FLASK
            var flaskposturl: String = "http://10.0.2.2:5000/predict"
            // https://stackoverflow.com/questions/30554702/cant-connect-to-flask-web-service-connection-refused
            // https://stackoverflow.com/questions/65467434/okhttp-unable-to-connect-to-a-localhost-endpoint-throws-connected-failed-econnr
            val resp:Response = postRequest(imageString, flaskposturl) // should return {"recipes":[{"title"...}, {"title"...}, ...]}
            // https://newbedev.com/okhttp-library-networkonmainthreadexception-on-simple-post --> must post on different thread

//            // Runs model inference and gets result.
//            val obj: PyObject = pyo.callAttr("predict",imageString) // "helloworld"
//            Log.d("DEBUG", "THE OBJ IS $obj")
        })

        var goToRecipes:Button = findViewById(R.id.button3)
        goToRecipes.setOnClickListener(View.OnClickListener {
            val intent = Intent(this, RecipeListActivity::class.java)
            startActivity(intent)
        })
    }


    companion object {
        val MEDIA_TYPE_MARKDOWN = "text/x-markdown; charset=utf-8".toMediaType() // string
        val MEDIA_TYPE_PLAINTEXT = "text/plain; charset=utf-8".toMediaType() // bytes
        val MEDIA_TYPE_JSON = "application/json; charset=utf-8".toMediaType() // json??
    }
    private fun postRequest(message: String, URL: String): Response {
        val okHttpClient = OkHttpClient()
        // https://howtoprogram.xyz/2017/01/14/how-to-post-with-okhttp/
        val request: Request = Request.Builder()
            .post(message.toRequestBody(MEDIA_TYPE_PLAINTEXT))
            .url(URL)
            .build()

        if (request != null) {
            okHttpClient.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    e.printStackTrace()
                }

                override fun onResponse(call: Call, response: Response) {
                    val response = runOnUiThread(Runnable {
                        Log.d("DEBUG","IN THE RUNNABLE")
                         fun run(): Response {
                             if (!response.isSuccessful) throw IOException("Unexpected code $response")
                             for ((name, value) in response.headers) {
                                 Log.d("DEBUG","$name: $value")
                             }
                             Log.d("DEBUG", response.body!!.string())
                             try {
                                 return response
//                                 Toast.makeText(
//                                     this@MainActivity,
//                                     response.body!!.string(),
//                                     Toast.LENGTH_LONG
//                                 ).show()
                             } catch (e: IOException) {
                                 Log.d("DEBUG","cannot toast")
                                 e.printStackTrace()
                             }
                        }
                    })
//                    response.use {
//                        if (!response.isSuccessful) throw IOException("Unexpected code $response")
//                        for ((name, value) in response.headers) {
//                            Log.d("DEBUG","$name: $value")
//                        }
//                        Log.d("DEBUG", response.body!!.string())
//                    }
                }
            })
        }
        return response
    }
    private fun getImageString(bitmap: Bitmap): String{
        var baos: ByteArrayOutputStream = ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos)
        val imageBytes: ByteArray = baos.toByteArray()
        Log.d("DEBUG", "imageBytes type "+imageBytes.javaClass.kotlin.simpleName)
        val imageString:String = android.util.Base64.encodeToString(imageBytes, Base64.DEFAULT)
        Log.d("DEBUG", imageString.substring(0, 20))
        return imageString
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        imgview.setImageURI(data?.data)

        var uri: Uri?= data?.data
        bitmap = MediaStore.Images.Media.getBitmap(this.contentResolver, uri)

    }
}