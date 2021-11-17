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
import com.example.myapplication.ml.CnnKnnModelSmall

import org.tensorflow.lite.DataType
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    lateinit var bitmap: Bitmap
    lateinit var imgview: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        imgview = findViewById(R.id.imageView)

        var tv:TextView = findViewById(R.id.textView)


        var select: Button = findViewById(R.id.button)
        select.setOnClickListener(View.OnClickListener {
            var intent: Intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(intent, 100)

            tv.setText("Click on Predict!")
        })

        var predict:Button = findViewById(R.id.button2)
        predict.setOnClickListener(View.OnClickListener {

            var resized: Bitmap = Bitmap.createScaledBitmap(bitmap, 299, 299, true)
            val model = CnnKnnModelSmall.newInstance(this)
            var tImage = TensorImage(DataType.FLOAT32)
            tImage.load(resized)
            var byteBuffer = tImage.tensorBuffer

        // Runs model inference and gets result.
            val outputs = model.process(byteBuffer)
            val outputFeature0 = outputs.outputFeature0AsTensorBuffer


            Log.i("outputFeature0", outputFeature0.intArray.contentToString())
//            tv.setText(max.toString())
            val intent = Intent(this, RecipeListActivity::class.java)
            intent.putExtra("similarity",outputFeature0.intArray)
            startActivity(intent)

// Releases model resources if no longer used.
            model.close()
        })

        var goToRecipes:Button = findViewById(R.id.button3)
        goToRecipes.setOnClickListener(View.OnClickListener {
            val intent = Intent(this, RecipeListActivity::class.java)
            startActivity(intent)
        })
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        imgview.setImageURI(data?.data)

        var uri: Uri?= data?.data
        bitmap = MediaStore.Images.Media.getBitmap(this.contentResolver, uri)

    }

//    fun getMax(arr:FloatArray): Int {
//        var ind = 0
//        var min = 0.0f
//        for (i in 0..5) {
//            if (arr[i] > min) {
//                ind = i
//                min = arr[i]
//            }
//        }
//        return ind
//    }
}