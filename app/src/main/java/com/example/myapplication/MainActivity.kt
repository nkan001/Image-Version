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
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.example.myapplication.databinding.ActivityMainBinding
import java.io.ByteArrayOutputStream
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    lateinit var bitmap: Bitmap
    lateinit var imgview: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // https://www.youtube.com/watch?v=27kdAqDUpcE&ab_channel=ProgrammingFever
        if (! Python.isStarted()) {
            Python.start(AndroidPlatform(this));
        }
        var py: Python = Python.getInstance();
        var pyo: PyObject = py.getModule("predict")//"hello")
        Log.d("DEBUG", "Got the python module $pyo")

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
            Log.d("DEBUG","PREDICT WAS CLICKED")
            val imageString: String= getImageString(bitmap)

            Log.d("DEBUG", "CALLING PREDICT NOW")
            // Runs model inference and gets result.
            val obj: PyObject = pyo.callAttr("predict",imageString) // "helloworld"
            Log.d("DEBUG", "THE OBJ IS $obj")
        })

        var goToRecipes:Button = findViewById(R.id.button3)
        goToRecipes.setOnClickListener(View.OnClickListener {
            val intent = Intent(this, RecipeListActivity::class.java)
            startActivity(intent)
        })
    }
    private fun getImageString(bitmap: Bitmap): String{
        var baos: ByteArrayOutputStream = ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos)
        val imageBytes: ByteArray = baos.toByteArray()
        val imageString:String = android.util.Base64.encodeToString(imageBytes, Base64.DEFAULT)
        return imageString
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        imgview.setImageURI(data?.data)

        var uri: Uri?= data?.data
        bitmap = MediaStore.Images.Media.getBitmap(this.contentResolver, uri)

    }
}