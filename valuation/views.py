import joblib
import pandas as pd

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from .models import PropertyValuation


# =========================================================
# LOAD MACHINE LEARNING MODEL
# =========================================================

MODEL_PATH = (
    settings.BASE_DIR
    / "valuation"
    / "ml_models"
    / "nepal_gharjagga_model.joblib"
)

model = joblib.load(MODEL_PATH)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_nepali_currency(amount):
    """
    Format a numerical amount into a readable
    Nepali currency representation.
    """

    if amount >= 1000000000:
        return f"Rs. {amount / 1000000000:.2f} Arab"

    if amount >= 10000000:
        return f"Rs. {amount / 10000000:.2f} Crore"

    if amount >= 100000:
        return f"Rs. {amount / 100000:.2f} Lakh"

    return f"Rs. {amount:,.0f}"


# =========================================================
# HOME
# =========================================================

def home(request):
    return render(
        request,
        "valuation/home.html"
    )


# =========================================================
# ABOUT
# =========================================================

def about(request):
    return render(
        request,
        "valuation/about.html"
    )


# =========================================================
# SIGN UP
# =========================================================

def signup(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = UserCreationForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        user = form.save()

        login(
            request,
            user
        )

        messages.success(
            request,
            "Your account has been created successfully."
        )

        return redirect("dashboard")

    return render(
        request,
        "registration/signup.html",
        {
            "form": form
        }
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    # Only active valuations are shown.
    # Deleted valuations are excluded.

    valuations = (
        PropertyValuation.objects
        .filter(
            user=request.user,
            is_deleted=False
        )
    )

    recent_valuations = (
        valuations
        .order_by("-created_at")[:5]
    )

    total = valuations.count()

    latest = valuations.first()

    average_value = None

    if total:

        average_value = (
            sum(
                float(
                    valuation.predicted_price_npr
                )
                for valuation in valuations
            )
            / total
        )

    return render(
        request,
        "valuation/dashboard.html",
        {
            "total_valuations": total,

            "latest": latest,

            "average_value": (
                format_nepali_currency(
                    average_value
                )
                if average_value
                else "—"
            ),

            "recent_valuations":
                recent_valuations,

            # Keep these names as well so your
            # existing dashboard template remains
            # compatible.

            "valuations":
                recent_valuations,

            "total":
                total,
        }
    )


# =========================================================
# AI PROPERTY VALUATION
# =========================================================

@login_required
def valuation(request):

    result = None

    if request.method == "POST":

        try:

            location = request.POST.get(
                "location",
                "New Baneshwor, Kathmandu"
            )

            land_aana = float(
                request.POST.get(
                    "land_aana",
                    4.0
                )
            )

            floors = float(
                request.POST.get(
                    "floors",
                    2.5
                )
            )

            road_feet = float(
                request.POST.get(
                    "road_feet",
                    13
                )
            )

            road_type = request.POST.get(
                "road_type",
                "Pitch"
            )

            rooms = int(
                request.POST.get(
                    "rooms",
                    6
                )
            )

            bathrooms = int(
                request.POST.get(
                    "bathrooms",
                    3
                )
            )


            # ---------------------------------------------
            # PREPARE DATA FOR MACHINE LEARNING MODEL
            # ---------------------------------------------

            input_data = pd.DataFrame(
                [{
                    "location": location,
                    "land_aana": land_aana,
                    "floors": floors,
                    "road_feet": road_feet,
                    "road_type": road_type,
                    "rooms": rooms,
                    "bathrooms": bathrooms,
                }]
            )


            # ---------------------------------------------
            # ML PREDICTION
            # ---------------------------------------------

            predicted_price = float(
                model.predict(
                    input_data
                )[0]
            )


            # ---------------------------------------------
            # RENT & CAP RATE
            # ---------------------------------------------

            monthly_rent = (
                predicted_price * 0.0035
            )

            annual_rent = (
                monthly_rent * 12
            )

            cap_rate = (
                annual_rent
                * 0.85
                / predicted_price
            ) * 100


            # ---------------------------------------------
            # 5-YEAR FORECAST
            # ---------------------------------------------

            forecast_labels = [
                f"Year {i}"
                for i in range(1, 6)
            ]

            forecast_values = [
                round(
                    predicted_price
                    * ((1 + 0.075) ** i)
                )
                for i in range(1, 6)
            ]


            # ---------------------------------------------
            # FORMAT PRICE
            # ---------------------------------------------

            price_formatted = (
                format_nepali_currency(
                    predicted_price
                )
            )


            # ---------------------------------------------
            # SAVE VALUATION
            # ---------------------------------------------

            PropertyValuation.objects.create(

                user=request.user,

                location=location,

                land_aana=land_aana,

                floors=floors,

                road_feet=int(
                    road_feet
                ),

                road_type=road_type,

                rooms=rooms,

                bathrooms=bathrooms,

                predicted_price_npr=
                    predicted_price,

                price_formatted=
                    price_formatted,

                monthly_rent_npr=
                    monthly_rent,

                cap_rate=
                    f"{cap_rate:.2f}%",

            )


            # ---------------------------------------------
            # RESULT FOR TEMPLATE
            # ---------------------------------------------

            result = {

                "price_formatted":
                    price_formatted,

                "predicted_price_npr":
                    f"Rs. {predicted_price:,.0f}",

                "price_low":
                    format_nepali_currency(
                        predicted_price * 0.95
                    ),

                "price_high":
                    format_nepali_currency(
                        predicted_price * 1.05
                    ),

                "monthly_rent":
                    format_nepali_currency(
                        monthly_rent
                    ),

                "cap_rate":
                    f"{cap_rate:.2f}%",

                "forecast_labels":
                    forecast_labels,

                "forecast_values":
                    forecast_values,

                "inputs":
                    request.POST,

            }


            messages.success(
                request,
                "Property valuation completed successfully."
            )


        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter valid property values."
            )


    return render(
        request,
        "valuation/valuation.html",
        {
            "result": result
        }
    )


# =========================================================
# ACTIVE VALUATION HISTORY
# =========================================================

@login_required
def history(request):

    valuations = (
        PropertyValuation.objects
        .filter(
            user=request.user,
            is_deleted=False
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "valuation/history.html",
        {
            "valuations": valuations
        }
    )


# =========================================================
# RECENTLY DELETED
# =========================================================

@login_required
def deleted_history(request):

    deleted_valuations = (
        PropertyValuation.objects
        .filter(
            user=request.user,
            is_deleted=True
        )
        .order_by("-deleted_at")
    )

    return render(
        request,
        "valuation/deleted_history.html",
        {
            "valuations": deleted_valuations
        }
    )


# =========================================================
# MOVE VALUATION TO RECENTLY DELETED
# =========================================================

@login_required
def delete_valuation(
    request,
    valuation_id
):

    # Only POST requests are allowed.
    if request.method != "POST":
        return redirect("history")


    # IMPORTANT:
    # The valuation must belong to the
    # currently logged-in user.

    valuation = get_object_or_404(
        PropertyValuation,
        id=valuation_id,
        user=request.user,
        is_deleted=False,
    )


    # Soft delete
    valuation.is_deleted = True

    valuation.deleted_at = timezone.now()


    valuation.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
        ]
    )


    messages.success(
        request,
        "Valuation moved to Recently Deleted."
    )


    return redirect("history")


# =========================================================
# RESTORE VALUATION
# =========================================================

@login_required
def restore_valuation(
    request,
    valuation_id
):

    # Only POST requests are allowed.
    if request.method != "POST":
        return redirect("deleted_history")


    valuation = get_object_or_404(
        PropertyValuation,
        id=valuation_id,
        user=request.user,
        is_deleted=True,
    )


    # Restore the valuation.
    valuation.is_deleted = False

    valuation.deleted_at = None


    valuation.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
        ]
    )


    messages.success(
        request,
        "Valuation restored successfully."
    )


    return redirect("deleted_history")


# =========================================================
# PERMANENTLY DELETE VALUATION
# =========================================================

@login_required
def permanently_delete_valuation(
    request,
    valuation_id
):

    # Only POST requests are allowed.
    if request.method != "POST":
        return redirect("deleted_history")


    valuation = get_object_or_404(
        PropertyValuation,
        id=valuation_id,
        user=request.user,
        is_deleted=True,
    )


    # This permanently removes the database record.
    valuation.delete()


    messages.success(
        request,
        "Valuation permanently deleted."
    )


    return redirect("deleted_history")