package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.widget.*

class RecipeListActivity : AppCompatActivity() {

    private lateinit var adapter: ArrayAdapter<*>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_recipe_list)

        val actionBar = supportActionBar

        if (actionBar != null) {
            actionBar.title = "Recipe List"
            actionBar.setDisplayHomeAsUpEnabled(true)
        }

        Log.i("TESTING1", "GOING TO RUN RECIPELIST")
        val recipeList = Recipe.getRecipesFromFile("real_ingredients_2.json", this)
        Log.i("TESTING2", "DID RECIPELISTRUN")
//        val listItems = arrayOfNulls<String>(recipeList.size)
//
//        for (i in 0 until recipeList.size){
//            val recipe = recipeList[i]
//            listItems[i] = recipe.title
//        }
//
//        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listItems)
        val listView = findViewById<ListView>(R.id.lv_listView)
//        val emptyTextView = findViewById<TextView>(R.id.tv_emptyTextView)
//
//        listView.adapter = adapter
//        listView.onItemClickListener = AdapterView.OnItemClickListener{ parent, view, position, id ->
//            Toast.makeText(applicationContext, parent?.getItemAtPosition(position).toString(), Toast.LENGTH_SHORT).show()
//        }
//        listView.emptyView = emptyTextView

        val adapter = RecipeAdapter(this, recipeList)
        listView.adapter = adapter

        val context = this
        listView.setOnItemClickListener { _, _, position, _ ->
            val selectedRecipe = recipeList[position]
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
                adapter.filter.filter(newText)
                return true
            }
        })

        return super.onCreateOptionsMenu(menu)
    }
}