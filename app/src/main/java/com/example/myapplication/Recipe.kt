package com.example.myapplication

import android.content.Context
import org.json.JSONException
import org.json.JSONObject


class Recipe(
    val title: String,
    val description: String,
    val imageUrl: String,
    val instructionUrl: String,
    val label: String,
    val ratings: Double,
    val eggFree: Boolean,
    val dairyFree: Boolean,
    val nutFree: Boolean,
    val shellFishFree: Boolean,
    val vegetarian: Boolean,
    val vegan: Boolean) {


    companion object {

        fun getRecipesFromFileORJSON(filename: String, context: Context, mode: String): ArrayList<Recipe> {
            val recipeList = ArrayList<Recipe>()

            try {
                // Load data
                var jsonString = filename
                if(mode == "file") {
                    jsonString = loadJsonFromAsset("real_ingredients_2.json", context)
                }
                val json = JSONObject(jsonString)
                val recipes = json.getJSONArray("recipes")

                // Get Recipe objects from data
                (0 until recipes.length()).mapTo(recipeList) {
                    Recipe(
                        cleanTitle(recipes.getJSONObject(it).getString("title")),
                        recipes.getJSONObject(it).getString("description"),
                        recipes.getJSONObject(it).getString("image"),
                        recipes.getJSONObject(it).getString("url"),
                        recipes.getJSONObject(it).getString("dietLabel"),
                        recipes.getJSONObject(it).getDouble("ratings"),
                        recipes.getJSONObject(it).getBoolean("egg_free"),
                        recipes.getJSONObject(it).getBoolean("dairy_free"),
                        recipes.getJSONObject(it).getBoolean("nut_free"),
                        recipes.getJSONObject(it).getBoolean("shellfish_free"),
                        recipes.getJSONObject(it).getBoolean("vegetarian"),
                        recipes.getJSONObject(it).getBoolean("vegan")
                    )
                }

            } catch (e: JSONException) {
                e.printStackTrace()
            }

            return recipeList
        }

        /* Special symbols are observed to be encased between '&' and ';' characters
        *  This function removes the special characters
        * */
        private fun cleanTitle(title: String): String {
            return if(title.contains('&') && title.contains(';')) {
                val re = Regex("&.*?;")
                re.replace(title, "")
            } else {
                title
            }
        }

        private fun loadJsonFromAsset(filename: String, context: Context): String {
            var json: String? = null

            try {
                val inputStream = context.assets.open(filename)
                val size = inputStream.available()
                val buffer = ByteArray(size)
                inputStream.read(buffer)
                inputStream.close()
                json = String(buffer, Charsets.UTF_8)
            } catch (ex: java.io.IOException) {
                ex.printStackTrace()
                return "{}"
            }

            return json
        }
    }
}