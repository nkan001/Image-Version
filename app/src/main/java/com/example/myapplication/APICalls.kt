package com.example.myapplication

import android.app.Activity
import android.content.Context
import android.graphics.Bitmap
import android.util.Base64
import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.ByteArrayOutputStream
import java.io.IOException

class APICalls {

    companion object {
        val URL: String = "http://10.0.2.2:5000/predict"
        val MEDIA_TYPE_MARKDOWN = "text/x-markdown; charset=utf-8".toMediaType() // string
        val MEDIA_TYPE_PLAINTEXT = "text/plain; charset=utf-8".toMediaType() // bytes
        val MEDIA_TYPE_JSON = "application/json; charset=utf-8".toMediaType() // json??

        fun postRequest(message: String, context: Context, then: ((Response)->Unit)) {
            Log.d("DEBUG", "In postRequest")
            val okHttpClient = OkHttpClient()
            // https://howtoprogram.xyz/2017/01/14/how-to-post-with-okhttp/
            val request: Request = Request.Builder()
                .post(message.toRequestBody(MEDIA_TYPE_PLAINTEXT))
                .url(URL)
                .build()
//        if (request ==null) throw // TODO: throw something (the computer out of the window)
//                    response_global = okHttpClient.newCall(request).execute() // MUST BE ASYNC https://newbedev.com/okhttp-library-networkonmainthreadexception-on-simple-post
            okHttpClient.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    e.printStackTrace()
                }
                override fun onResponse(call: Call, response: Response) {
//                    (context as Activity).runOnUiThread {
                    response.use {
                        if (!response.isSuccessful) throw IOException("Unexpected code $response")
                        for ((name, value) in response.headers) {
                            Log.d("DEBUG","$name: $value")
                        }
                        then(response)
                    }
//                    }
                }
            })
        }
        fun getImageString(bitmap: Bitmap): String{
            val baos: ByteArrayOutputStream = ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos)
            var imageBytes: ByteArray = baos.toByteArray()
            Log.d("DEBUG", "imageBytes type "+imageBytes.javaClass.kotlin.simpleName)
            var imageString:String = android.util.Base64.encodeToString(imageBytes, Base64.DEFAULT)
            Log.d("DEBUG", imageString.substring(0, 20))
            return imageString
        }
    }
}