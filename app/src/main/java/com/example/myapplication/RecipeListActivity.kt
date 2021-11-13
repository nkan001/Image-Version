package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.widget.*

class RecipeListActivity : AppCompatActivity() {

    private lateinit var adapter: RecipeAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_recipe_list)

        val actionBar = supportActionBar

        if (actionBar != null) {
            actionBar.title = "Recipe List"
            actionBar.setDisplayHomeAsUpEnabled(true)
        }
//        val similarity=intent.getStringExtra("similarity")
        val similarity: IntArray? = intent.extras?.getIntArray("similarity")
        Log.i("similarity", similarity.contentToString())
        val recipeList = Recipe.getRecipesFromFile("all_recipes.json", this)
        Log.i("FirstRecipelist", recipeList[32].toString())
        recipeList.sortBy { it.ratings*it.ratingCounts }
        Log.i("TESTING2", "DID RECIPELISTRUN")

        val fileName = "labels.txt"
        val inputString = application.assets.open(fileName).bufferedReader().use {it.readText()}
        val labelsList = inputString.split("\n")

        val listItems = ArrayList<Recipe>()
        if (similarity != null) {
            for (i in similarity.indices) {
                val index = similarity[i].toInt()
                if (index<labelsList.size) {
                    val recipe = recipeList.filter { labelsList[index].contains(it.instructionUrl)}
                    if (recipe.isNotEmpty()) {
                        listItems.add(recipe[0])
                    }
                }
            }
        }
//        var listItemsIndex = 0

//        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listItems)
        val listView = findViewById<ListView>(R.id.lv_listView)
//        val emptyTextView = findViewById<TextView>(R.id.tv_emptyTextView)
//
//        listView.adapter = adapter
//        listView.onItemClickListener = AdapterView.OnItemClickListener{ parent, view, position, id ->
//            Toast.makeText(applicationContext, parent?.getItemAtPosition(position).toString(), Toast.LENGTH_SHORT).show()
//        }
//        listView.emptyView = emptyTextView
        adapter = RecipeAdapter(this, recipeList)

        if (similarity != null) {
            adapter.setDataSource(listItems)
        }
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
}