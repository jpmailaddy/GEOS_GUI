def destroy_children(parent):
    for widget in parent.winfo_children():
        widget.destroy()