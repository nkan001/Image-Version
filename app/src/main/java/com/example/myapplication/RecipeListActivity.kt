package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.View
import android.widget.*
import okhttp3.Response
import kotlin.collections.contains as contains
import okhttp3.ResponseBody


class RecipeListActivity : AppCompatActivity() {

    private lateinit var adapter: RecipeAdapter
    private val filterCategories = ArrayList<String>()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_recipe_list)

        val actionBar = supportActionBar

        if (actionBar != null) {
            actionBar.title = "Recipe List"
            actionBar.setDisplayHomeAsUpEnabled(true)
        }

        val similarity: String = intent.extras!!.getString("similarity")!!
        Log.i("similarity", similarity.toString())
        Log.i("TESTING1", "GOING TO RUN RECIPELIST")
        val recipeList = Recipe.getRecipesFromFileORJSON(similarity, this, "json")
        Log.i("TESTING2", "DID RECIPELISTRUN")

        val listView = findViewById<ListView>(R.id.lv_listView)

        adapter = RecipeAdapter(this, recipeList)
        listView.adapter = adapter

        val context = this
        listView.setOnItemClickListener { _, _, position, _ ->
            val selectedRecipe = adapter.getItem(position)
            val detailIntent = RecipeDetailActivity.newIntent(context, selectedRecipe)
            startActivity(detailIntent)
        }
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.nav_menu, menu)
        val search= menu?.findItem(R.id.nav_search)
        val searchView = search?.actionView as SearchView
        searchView.queryHint = "Search something!"

        searchView.setOnQueryTextListener(object: SearchView.OnQueryTextListener{
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            override fun onQueryTextChange(newText: String?): Boolean {
                Log.i("onQueryTextChange", newText.toString())
                adapter.filter.filter(newText)
//                adapter.notifyDataSetChanged()
                Log.i("onQueryTextChange", "Filtered")
                return true
            }
        })

        return super.onCreateOptionsMenu(menu)
    }

    fun callFilter(filterCategoryString: String){
        Log.i("beforefilterCategories", filterCategories.toString())
        if (filterCategories.contains(filterCategoryString)) {
            filterCategories.remove(filterCategoryString)
            Log.i("removedfilterCategories", filterCategories.toString())
        } else {
            filterCategories.add(filterCategoryString)
            Log.i("addedfilterCategories", filterCategories.toString())
        }
        Log.i("afterfilterCategories", filterCategories.toString())
        val message = filterCategories.joinToString { it -> "\'${it}\'" }
        Log.i("recipeLsitActivity", message)
        APICalls.postRequest(message, this){
            var response:Response = it
//            val responseBody = response.body!!.string()
            val responseBodyCopy = response.peekBody(Long.MAX_VALUE)
            val responseBody = responseBodyCopy.string()
            Log.i("ResponseBodyFilter", responseBody)
            val recipeList = Recipe.getRecipesFromFileORJSON(responseBody, this, "json")
            adapter.setDataSource(recipeList)
        }
    }

    fun eggFreeFilterTapped(view: android.view.View) {
        callFilter("egg_free")
    }

    fun dairyFreeFilterTapped(view: android.view.View) {
        callFilter("dairy_free")
    }

    fun nutFreeFilterTapped(view: android.view.View) {
        callFilter("nut_free")
    }

    fun shellfishFreeFilterTapped(view: android.view.View) {
        callFilter("shellfish_free")
    }

    fun vegetarianFilterTapped(view: android.view.View) {
        callFilter("vegetarian")
    }

    fun veganFilterTapped(view: android.view.View) {
        callFilter("vegan")
    }

}