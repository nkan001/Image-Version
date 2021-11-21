package com.example.myapplication

import android.app.Activity
import android.content.Context
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.core.content.res.ResourcesCompat
import com.squareup.picasso.Picasso
import kotlin.collections.ArrayList
import android.widget.ImageView
import android.widget.LinearLayout
import androidx.core.content.ContentProviderCompat.requireContext

class RecipeAdapter(private val contex: Context, private var dataSource: ArrayList<Recipe>): ArrayAdapter<Recipe>(contex, android.R.layout.simple_list_item_1, dataSource)
{

    private val inflater: LayoutInflater = contex.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
    var filtered = dataSource

    fun setDataSource(newDataSource: ArrayList<Recipe>) {
        filtered = newDataSource
//        contex
        (contex as Activity).runOnUiThread {
            notifyDataSetChanged()
        }
    }

    override fun getCount(): Int {
        return filtered.size
    }

    override fun getItem(position: Int): Recipe {
        return filtered[position]
    }

    override fun getItemId(position: Int): Long {
        return position.toLong()
    }

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        // Get view for row item
        val rowView = inflater.inflate(R.layout.list_item_recipe, parent, false)
        // Get title element
        val titleTextView = rowView.findViewById(R.id.recipe_list_title) as TextView
        // Get subtitle element
        val subtitleTextView = rowView.findViewById(R.id.recipe_list_subtitle) as TextView
        // Get detail element
        val detailTextView = rowView.findViewById(R.id.recipe_list_detail) as TextView
        // Get thumbnail element
        val thumbnailImageView = rowView.findViewById(R.id.recipe_list_thumbnail) as ImageView
        // Get diet element
        val linearForImage = rowView.findViewById(R.id.linearForImage) as LinearLayout
        // 1
        val recipe = getItem(position) as Recipe

        titleTextView.text = recipe.title
        subtitleTextView.text = recipe.description
        detailTextView.text = recipe.ratings.toString()

        for (i in 1..4){
            val imageView = ImageView(contex)
            imageView.layoutParams = LinearLayout.LayoutParams(90, 90) // value is in pixels
            if(recipe.eggFree && i == 1){
                imageView.setImageResource(R.mipmap.diet_icons_egg)
                linearForImage.addView(imageView)
            }
            if(recipe.dairyFree && i == 2){
                imageView.setImageResource(R.mipmap.diet_icons_dairy)
                linearForImage.addView(imageView)
            }
            if(recipe.nutFree && i == 3){
                imageView.setImageResource(R.mipmap.diet_icons_nuts)
                linearForImage.addView(imageView)
            }
            if(recipe.shellFishFree && i == 4){
                imageView.setImageResource(R.mipmap.diet_icons_shellfish)
                linearForImage.addView(imageView)
            }
        }

        Picasso.get().load(recipe.imageUrl).placeholder(R.mipmap.ic_launcher).into(thumbnailImageView)

        val titleTypeFace = ResourcesCompat.getFont(contex, R.font.josefinsans_bold)
        titleTextView.typeface = titleTypeFace

        val subtitleTypeFace = ResourcesCompat.getFont(contex, R.font.josefinsans_semibolditalic)
        subtitleTextView.typeface = subtitleTypeFace

        val detailTypeFace = ResourcesCompat.getFont(contex, R.font.quicksand_bold)
        detailTextView.typeface = detailTypeFace

        return rowView
    }


    override fun getFilter() = filter

    private var filter: Filter = object : Filter() {

        override fun performFiltering(constraint: CharSequence?): FilterResults {
            val results = FilterResults()

            val query = if (constraint != null && constraint.isNotEmpty()) autocomplete(constraint.toString())
            else arrayListOf()

            results.values = query
            results.count = query.size

            return results
        }

        private fun autocomplete(input: String): ArrayList<Recipe> {
            val results = arrayListOf<Recipe>()

            for (recip in dataSource) {
                if (recip.title.toLowerCase().contains(input.toLowerCase()))
                {results.add(recip)}
                else if (recip.description.toLowerCase().contains(input.toLowerCase()))
                {results.add(recip)}
                else if (recip.label.toLowerCase().contains(input.toLowerCase()))
                {results.add(recip)}
            }

            return results
        }

        override fun publishResults(constraint: CharSequence?, results: FilterResults) {
            filtered = results.values as ArrayList<Recipe>
            notifyDataSetChanged() //notifyDataSetInvalidated() //
        }

        override fun convertResultToString(result: Any) = (result as Recipe).title
    }


}