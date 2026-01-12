ConvertSegFinal = function (
    seg_,
    Res_L,
    org,
    des,
    frArmy,
    frArmyRT,
    NoAdt,
    NoChd,
    NoInf,
    FFare_L,
    isRT_,
    fareIdByFareSelected
) {
    GetFltDtl = function (key_) {
        if (Res_L != null && Res_L.dctFltDtl != null && key_ != null) {
            return Res_L.dctFltDtl[key_];
        }
    };

    GetAirLineName = function (key_) {
        if (Res_L != null && Res_L.C != null) {
            return Res_L.C[key_];
        }
    };
    GetAirportName = function (key_) {
        if (Res_L != null && Res_L.A != null) {
            if (Res_L.A[key_] != "" && Res_L.A[key_] != null) {
                return Res_L.A[key_];
            } else {
                return key_;
            }
            //return $scope.Res_L.A[key_];
        }
    };
    CountryName = function (key_) {
        if (Res_L != null && Res_L.A != null) {
            return Res_L.Cnty[key_];
        }
    };
    GetMonth = function (month) {
        const months = {
            Jan: "01",
            Feb: "02",
            Mar: "03",
            Apr: "04",
            May: "05",
            Jun: "06",
            Jul: "07",
            Aug: "08",
            Sep: "09",
            Oct: "10",
            Nov: "11",
            Dec: "12",
        };
        return months[month];
    };

    let Seg_L = {};
    Seg_L.id = seg_.id;
    Seg_L.BKID = seg_.BKID;
    Seg_L.segDTL = seg_.SD;
    Seg_L.segKey = seg_.SK;
    Seg_L.searchId = seg_.SID;
    Seg_L.ItineraryKey = seg_.IK;
    Seg_L.SearchOrigin = org;
    Seg_L.SearchDestination = des;
    Seg_L.DiscountAmount = seg_.DAMT;
    Seg_L.FareTypeInd = seg_.FTpInd;
    Seg_L.CpnTxtS = seg_.CpnTxtS;
    Seg_L.CCL = seg_.CCL;
    Seg_L.IACL = seg_.IACL;
    Seg_L.bonds = [];
    Seg_L.CT_UPG = "";
    FL = [];
    Seg_L.PT = seg_.PT;
    Seg_L.selectedFare = 0;
    fareId = fareIdByFareSelected; // change fareId according to fare selected
    Seg_L.FareTypeUI = 0;
    // if (getParameterByName("fn") != "") {
    //   Seg_L.FareTypeUI = parseInt(getParameterByName("fn"));
    // }
    // if (seg_.lstFr != null && seg_.lstFr != null && seg_.lstFr.length > 1) {
    //   if (isRT_) {
    //     var FareObjArr = document.getElementsByName(FareID_ + "fr" + seg_.SK);
    //     if (FareObjArr != null && FareObjArr.length > 0) {
    //       for (var i = 0; i < FareObjArr.length; i++) {
    //         if (FareObjArr[i].checked) {
    //           fareId = parseInt(FareObjArr[i].getAttribute("fr"));
    //           break;
    //         }
    //       }
    //     }
    //   } else {
    //     var FareObjArr = document.getElementsByName("fr" + seg_.SK);
    //     if (FareObjArr != null && FareObjArr.length > 0) {
    //       for (var i = 0; i < FareObjArr.length; i++) {
    //         if (FareObjArr[i].checked) {
    //           fareId = parseInt(FareObjArr[i].getAttribute("fr"));
    //           break;
    //         }
    //       }
    //     }
    //   }
    // }
    var idFareBK = "";
    var isHndBGG = false;
    if (seg_.b != null && seg_.b.length > 0) {
        for (var bc = 0; bc < seg_.b.length; bc++) {
            Bnd_L = {};
            Bnd_L.bndDTL = seg_.b[bc].BDT;
            if (seg_.b[bc].dctCanPo != null) {
                Bnd_L.dctCanPo = seg_.b[bc].dctCanPo;
            }

            Bnd_L.Legs = [];
            if (seg_.b[bc].FL != null && seg_.b[bc].FL.length > 0) {
                FL = seg_.b[bc].FL;
                //Seg_L.searchId = FL.SID;
            } else if (seg_.l_OB != null && seg_.l_OB.length > 0) {
                FL = seg_.l_OB[0].FL;
            }
            for (var lc = 0; lc < seg_.b[bc].FL.length; lc++) {
                var fleg = GetFltDtl(seg_.b[bc].FL[lc]);
                fLeg_L = {};
                fLeg_L.airName = GetAirLineName(fleg.AC);
                fLeg_L.org =
                    fleg.OG + "|" + GetAirportName(fleg.OG) + "|" + CountryName(fleg.OG);
                fLeg_L.dest =
                    fleg.DT + "|" + GetAirportName(fleg.DT) + "|" + CountryName(fleg.DT);
                fLeg_L.depDT = fleg.DDT;

                if (fleg.DDT.split("-").length > 1) {
                    DepDate = fleg.DDT.split("-")[1];
                    var month = GetMonth(DepDate.substring(2, 5));
                    var DepDate = new Date(
                        DepDate.substring(5, 9),
                        month,
                        DepDate.substring(0, 2)
                    );
                    //if ((seg_.EID == 0 || seg_.EID == 10) && DepDate <= new Date("2020-08-31")) {
                    if (
                        DepDate <= new Date("2020-09-30") &&
                        (seg_.EID != 5 || seg_.EID != 10 || seg_.EID != 1)
                    ) {
                        fLeg_L.HBU = "KG";
                        //fLeg_L.HBW=0;
                        fLeg_L.HBW = 7;
                    } else {
                        fLeg_L.HBU = "KG";
                        fLeg_L.HBW = 7;
                    }
                    if (seg_.EID == 1) {
                        fLeg_L.HBU = "KG";
                        fLeg_L.HBW = 7;
                    }
                    if (seg_.EID == 0 && DepDate <= new Date("2020-12-31")) {
                        fLeg_L.HBU = "KG";
                        //fLeg_L.HBW=0;
                        fLeg_L.HBW = 7;
                    }
                    if (seg_.EID == 0) {
                        //fLeg_L.HBU="KG";
                        //fLeg_L.HBW=0;
                    }
                    if (seg_.EID == 31) {
                        fLeg_L.HBU = "KG";
                        fLeg_L.HBW = 5;
                    }
                }
                fLeg_L.HBU = fleg.HBU;
                fLeg_L.HBW = fleg.HBW;

                fLeg_L.arrDT = fleg.ADT;
                fLeg_L.depTM = fleg.DTM;
                fLeg_L.arrTM = fleg.ATM;
                fLeg_L.fltNum = fleg.FN;
                fLeg_L.airCode = fleg.AC;
                fLeg_L.stops = fleg.STP;
                fLeg_L.currCode = fleg.CC;
                fLeg_L.cabin = fleg.CB;
                fLeg_L.duration = fleg.DUR;
                fLeg_L.depTer = fleg.DTER;
                fLeg_L.arrTer = fleg.ATER;
                fLeg_L.fareCls = seg_.b[bc].lFC[lc]; //fleg.FCLS;
                fLeg_L.LyOvr = fleg.LOV;
                if (lc > 0 && seg_.b[bc].LLOV != null) {
                    fLeg_L.LyOvr = seg_.b[bc].LLOV[lc - 1];
                }
                fLeg_L.Group = fleg.GRP;
                fLeg_L.AircraftType = fleg.ACTYP;
                fLeg_L.AirSeat = fleg.AST;
                fLeg_L.LayoverAt = fleg.LOVAT;
                fLeg_L.LayoverDuration = fleg.LOVDU;
                fLeg_L.OperatedBy = fleg.OPB;
                if (seg_.b[bc].lstBagg.length > lc) {
                    fLeg_L.BaggageUnit = seg_.b[bc].lstBagg[lc].split("|")[0]; //fleg.BU;
                    fLeg_L.BaggageWeight = seg_.b[bc].lstBagg[lc].split("|")[1];
                }

                if (seg_.b[bc].lstHBagg != null && seg_.b[bc].lstHBagg.length > lc) {
                    fLeg_L.HBU = seg_.b[bc].lstHBagg[lc].split("|")[0]; //fleg.BU;
                    fLeg_L.HBW = seg_.b[bc].lstHBagg[lc].split("|")[1]; //fleg.BU;
                }

                fLeg_L.EquipmentType = fleg.ET;
                fLeg_L.SeatAvail = fleg.SA;
                fLeg_L.FlightDetailRefKey = fleg.FlightDetailRefKey;
                fLeg_L.ProviderCode = "";
                if (
                    seg_.b[bc].dctBKKY != null &&
                    Object.values(seg_.b[bc].dctBKKY).length > fareId
                ) {
                    //&& seg_.b[bc].dctBKKY.length > 0 && seg_.b[bc].dctBKKY.length > lc
                    idFareBK = seg_.lstFr[fareId].fs;
                    if (seg_.b[bc].dctBKKY[idFareBK].length > lc) {
                        fLeg_L.ProviderCode = seg_.b[bc].dctBKKY[idFareBK][lc]; //seg_.b[bc].dctBKKY[fareId];//fleg.ProviderCode;
                        fLeg_L.BaggageUnit = seg_.b[bc].dctBagg[idFareBK][lc].split("|")[0]; //fleg.BU;
                        fLeg_L.BaggageWeight =
                            seg_.b[bc].dctBagg[idFareBK][lc].split("|")[1];
                    }
                } else if (seg_.b[bc].BkKY != null) {
                    fLeg_L.ProviderCode = seg_.b[bc].BkKY[lc]; //fleg.ProviderCode;
                } else {
                    fLeg_L.ProviderCode = fleg.ProviderCode;
                }
                // fLeg_L.ProviderCode = fleg.ProviderCode;
                Bnd_L.Legs.push(fLeg_L);
            }

            Bnd_L.Refundable = seg_.RF == true ? "Refundable" : "Non-Refundable"; //seg_.b[bc].RF == "1" ? 'Refundable' : 'Non-Refundable';
            if (seg_.lstFr != null && seg_.lstFr.length > 0) {
                Bnd_L.Refundable =
                    seg_.lstFr[fareId].L_PF[0].RF == "True"
                        ? "Refundable"
                        : "Non-Refundable";
                Bnd_L.IsBaggageFare = seg_.lstFr[fareId].IsHB;
                seg_.l_HB = seg_.lstFr[fareId].IsHB;
                isHndBGG = seg_.lstFr[fareId].IsHB;
            }

            try {
                if (parseInt(seg_.lstFr[fareId].L_PF[0].BW) > 0) {
                    Bnd_L.IsBaggageFare = false;
                    // seg_.l_HBT=false;
                    isHndBGG = false;
                }
                // if (document.getElementById(fleg.AC + fleg.FN) != null) {
                //   fLeg_L.co2 = document.getElementById(fleg.AC + fleg.FN).innerHTML;
                // }
            } catch (e) { }
            Bnd_L.JrnyTm = seg_.b[bc].JyTm;
            Bnd_L.ConnType = seg_.b[bc].CT;
            if (seg_.b[bc].dctCanPo != null) {
                try {
                    Bnd_L.lstCanPo = seg_.b[bc].dctCanPo[idFareBK];
                } catch (e) { }
            }
            Seg_L.bonds.push(Bnd_L);
        }
    }
    Seg_L.Fare = null;
    if (seg_.lstFr != null && seg_.lstFr.length > 0) {
        seg_.Fr = seg_.lstFr[fareId];
        if (
            !(frArmy == "9" || frArmy == "10" || frArmy == "11" || frArmy == "21")
        ) {
            if (frArmyRT != "") {
                frArmyRT += ",";
            }
            frArmy = seg_.lstFr[fareId].FId;
            frArmyRT += seg_.lstFr[fareId].FId;
        } else {
            if (frArmyRT != "") {
                frArmyRT += ",";
            }
            frArmyRT += seg_.lstFr[fareId].FId;
        }
        Seg_L.INSP = seg_.lstFr[fareId].INSP;
        if (
            seg_.lstFr[fareId].CT_UPG != null &&
            seg_.lstFr[fareId].CT_UPG != null
        ) {
            Seg_L.CT_UPG = seg_.lstFr[fareId].CT_UPG;
        }

        Seg_L.INSAmtPP = seg_.lstFr[fareId].L_PF[0].INSAmtPP;
        try {
            Seg_L.INSAmtKey = seg_.lstFr[fareId].FIAK;
        } catch (e) { }
        Seg_L.FIA = seg_.lstFr[fareId].FIA;
        Seg_L.lstFr = seg_.lstFr;
        Seg_L.selectedFare = fareId;

        Seg_L.FN = seg_.lstFr[fareId].FN;
        //Seg_L.ItineraryKey = seg_.lstFr[fareId].IK;
        Seg_L.ItineraryKey = seg_.lstFr[fareId].ItnanaryKey;
        if (seg_.lstFr[fareId].CouponCodeList != null) {
            Seg_L.CCL = seg_.lstFr[fareId].CouponCodeList;
            Seg_L.IACL = seg_.lstFr[fareId].isAddCL;
            Seg_L.CpnTxtS = seg_.lstFr[fareId].CpnTxtS;
            Seg_L.CpnLstDis = seg_.lstFr[fareId].DA; //seg_.DAMT;
            try {
                if (seg_.I_RT != null && seg_.I_RT == true) {
                    Seg_L.CpnLstDis = 0;
                    Seg_L.CCL = "";
                    Seg_L.IACL = false;
                    Seg_L.CpnTxtS = "";
                }
            } catch (e) { }
        } else if (seg_.lstFr[fareId].CC != "") {
            Seg_L.DiscountAmount = seg_.lstFr[fareId].DA; //seg_.DAMT;
        }

        if (seg_.Fr.BDKEY != null) {
            Seg_L.brandFareKey = seg_.Fr.BDKEY;
        }
    }
    var totalExSeatFare = 0;
    if (seg_.Fr != null) {
        Seg_L.Fare = {};
        Seg_L.Fare.lstPxPF = [];
        var adult = 0;
        var child = 0;
        var infant = 0;

        var adultT = 0;
        var childT = 0;
        var infantT = 0;

        var TotalTF = 0;
        var TotalTT = 0;
        var TotalMRKP = 0;
        var STF = 0;
        var TDS = 0;
        var ServiceFee = 0;
        var CashBack = 0;
        var Commission = 0;
        var TransactionFees = 0;
        if (seg_.Fr.SID != "") {
            Seg_L.searchId = seg_.Fr.SID;
        }
        if (seg_.Fr.L_PF != null && seg_.Fr.L_PF.length > 0) {
            for (var pxfrC = 0; pxfrC < seg_.Fr.L_PF.length; pxfrC++) {
                PxFare_L = {};
                PxFare_L.BaggUnit = seg_.Fr.L_PF[pxfrC].BU;
                PxFare_L.BaggWeight = seg_.Fr.L_PF[pxfrC].BW;
                PxFare_L.CanPenlty = seg_.Fr.L_PF[pxfrC].CNP;
                PxFare_L.ChanPenlty = seg_.Fr.L_PF[pxfrC].CHP;
                PxFare_L.FrBassCode = seg_.Fr.L_PF[pxfrC].FBC;
                PxFare_L.MarkUP = seg_.Fr.L_PF[pxfrC].MKP;
                PxFare_L.PaxType = seg_.Fr.L_PF[pxfrC].PT;
                PxFare_L.Refundable = seg_.Fr.L_PF[pxfrC].RF;
                PxFare_L.ESF = seg_.Fr.L_PF[pxfrC].ESF;
                if (seg_.Fr.L_PF[pxfrC].ESF != null) {
                    totalExSeatFare = totalExSeatFare + seg_.Fr.L_PF[pxfrC].ESF;
                }
                if (seg_.Fr.L_PF[pxfrC].PT.toUpperCase() == "ADULT") {
                    adult += seg_.Fr.L_PF[pxfrC].BF * NoAdt;
                    TotalTF += seg_.Fr.L_PF[pxfrC].TF * NoAdt;
                    TotalTT += seg_.Fr.L_PF[pxfrC].TTX * NoAdt;
                    adultT += seg_.Fr.L_PF[pxfrC].TTX * NoAdt;
                    TotalMRKP += seg_.Fr.L_PF[pxfrC].MKP * NoAdt;
                    if (seg_.Fr.L_PF[pxfrC].COM != null) {
                        Commission += seg_.Fr.L_PF[pxfrC].COM * NoAdt;
                    }
                    if (seg_.Fr.L_PF[pxfrC].CB != null) {
                        CashBack += seg_.Fr.L_PF[pxfrC].CB * NoAdt;
                    }
                    STF += 0;
                    if (seg_.Fr.L_PF[pxfrC].TDS != null) {
                        TDS += seg_.Fr.L_PF[pxfrC].TDS * NoAdt;
                    }
                    if (seg_.Fr.L_PF[pxfrC].SF != null) {
                        ServiceFee += seg_.Fr.L_PF[pxfrC].SF * NoAdt;
                    }
                    if (seg_.Fr.L_PF[pxfrC].TA != null) {
                        TransactionFees += seg_.Fr.L_PF[pxfrC].TA * NoAdt;
                    }
                } else if (seg_.Fr.L_PF[pxfrC].PT.toUpperCase() == "CHILD") {
                    child += seg_.Fr.L_PF[pxfrC].BF * NoChd; // + (seg_.Fr.L_PF[pxfrC].TF * NoChd) + (seg_.Fr.L_PF[pxfrC].TT * NoChd);
                    TotalTF += seg_.Fr.L_PF[pxfrC].TF * NoChd;
                    TotalTT += seg_.Fr.L_PF[pxfrC].TTX * NoChd;
                    childT += seg_.Fr.L_PF[pxfrC].TTX * NoChd;
                    TotalMRKP += seg_.Fr.L_PF[pxfrC].MKP * NoChd;
                    if (seg_.Fr.L_PF[pxfrC].COM != null) {
                        Commission += seg_.Fr.L_PF[pxfrC].COM * NoChd;
                    }
                    if (seg_.Fr.L_PF[pxfrC].CB != null) {
                        CashBack += seg_.Fr.L_PF[pxfrC].CB * NoChd;
                    }

                    STF += 0;
                    if (seg_.Fr.L_PF[pxfrC].TDS != null) {
                        TDS += seg_.Fr.L_PF[pxfrC].TDS * NoChd;
                    }
                    if (seg_.Fr.L_PF[pxfrC].SF != null) {
                        ServiceFee += seg_.Fr.L_PF[pxfrC].SF * NoChd;
                    }
                    if (seg_.Fr.L_PF[pxfrC].TA != null) {
                        TransactionFees += seg_.Fr.L_PF[pxfrC].TA * NoChd;
                    }
                } else if (seg_.Fr.L_PF[pxfrC].PT.toUpperCase() == "INFANT") {
                    infant += seg_.Fr.L_PF[pxfrC].BF * NoInf; // + (seg_.Fr.L_PF[pxfrC].TF * NoInf) + (seg_.Fr.L_PF[pxfrC].TT * NoInf);
                    TotalTF += seg_.Fr.L_PF[pxfrC].TF * NoInf;
                    TotalTT += seg_.Fr.L_PF[pxfrC].TTX * NoInf;
                    infantT += seg_.Fr.L_PF[pxfrC].TTX * NoInf;
                    TotalMRKP += seg_.Fr.L_PF[pxfrC].MKP * NoInf;
                    if (seg_.Fr.L_PF[pxfrC].COM != null) {
                        Commission += seg_.Fr.L_PF[pxfrC].COM * NoInf;
                    }
                    if (seg_.Fr.L_PF[pxfrC].CB != null) {
                        CashBack += seg_.Fr.L_PF[pxfrC].CB * NoInf;
                    }
                    if (seg_.Fr.L_PF[pxfrC].COM != null) {
                        STF += 0;
                    }
                    if (seg_.Fr.L_PF[pxfrC].TDS != null) {
                        TDS += seg_.Fr.L_PF[pxfrC].TDS * NoInf;
                    }
                    if (seg_.Fr.L_PF[pxfrC].SF != null) {
                        ServiceFee += seg_.Fr.L_PF[pxfrC].SF * NoInf;
                    }
                    if (seg_.Fr.L_PF[pxfrC].TA != null) {
                        TransactionFees += seg_.Fr.L_PF[pxfrC].TA * NoInf;
                    }
                }
                PxFare_L.BscFr = seg_.Fr.L_PF[pxfrC].BF;
                PxFare_L.TtlFare = seg_.Fr.L_PF[pxfrC].TF;
                PxFare_L.TtlTax = seg_.Fr.L_PF[pxfrC].TTX;

                PxFare_L.PaxCount = seg_.Fr.L_PF[pxfrC].PXC;
                PxFare_L.dfValue = seg_.Fr.L_PF[pxfrC].dfValue;
                PxFare_L.lstTxDt = [];
                PxFare_L.IsZeroCancellation = seg_.Fr.L_PF[pxfrC].I_ZCAN;
                PxFare_L.ZeroCancellationCharge = seg_.Fr.L_PF[pxfrC].ZCC;
                PxFare_L.ZeroCancellationValidity = seg_.Fr.L_PF[pxfrC].ZCV;
                PxFare_L.RefundableIn = seg_.Fr.L_PF[pxfrC].RFIN;
                PxFare_L.BrandedServies = seg_.Fr.L_PF[pxfrC].BRSER;
                Seg_L.Fare.lstCancellationPcy = [];
            }
        }

        Seg_L.Fare.BscFr = seg_.Fr.BF;
        Seg_L.Fare.TtlFrWthMkp = seg_.Fr.TFRMP;
        Seg_L.Fare.TtlTxWthMkp = seg_.Fr.TTXMP;
        Seg_L.Fare.TTLFr = seg_.Fr.TF;
        Seg_L.Fare.lstTxDt = [];
        Seg_L.Fare.ttlDiscount = seg_.Fr.TTDIS;
        Seg_L.Fare.FareTypeID = seg_.Fr.FRTYPID;
        Seg_L.Fare.FareType = seg_.Fr.FRTYP;
        Seg_L.Fare.BrandKeys = seg_.Fr.BDKEY;
        Seg_L.Fare.Branded = seg_.Fr.L_Bran;
        Seg_L.Fare.FareRule = seg_.Fr.FR;
        Seg_L.Fare = FFare_L;
        //Seg_L.INSP =seg_.lstFr[fareId].INSP;
        Seg_L.AdultPrice = adult;
        Seg_L.ChildPrice = child;
        Seg_L.InfantPrice = infant;

        Seg_L.AdultPriceT = adultT;
        Seg_L.ChildPriceT = childT;
        Seg_L.InfantPriceT = infantT;

        Seg_L.TotalTax = TotalTT;
        Seg_L.TotalFare = TotalTF + TotalMRKP; //- totalExSeatFare;
        Seg_L.ESF = totalExSeatFare;
        Seg_L.MarkUP = TotalMRKP;
        Seg_L.ttlDiscount = TotalTF + TotalMRKP; //seg_.TTDIS;
        Seg_L.CancePenalty = seg_.CNP;
        Seg_L.ChangPenalty = seg_.CHP;
        Seg_L.Refundable = seg_.RF;
        Seg_L.RefundableIn = seg_.RFIN;
        Seg_L.SpecialSegKey = seg_.SSK;
        Seg_L.ConnType = seg_.CT;
        if (Seg_L.bonds[0].lstCanPo != null) {
            Seg_L.lstCanPo = Seg_L.bonds[0].lstCanPo;
        } else {
            Seg_L.lstCanPo = seg_.LCP;
        }
        seg_.CBAMT = CashBack;
        seg_.Comm = Commission;
        seg_.TDS = TDS;
        seg_.SF = ServiceFee;
    } else {
        Seg_L.AdultPrice = seg_.AP;
        if (seg_.APT != null) {
            Seg_L.AdultPriceT = seg_.APT;
        }
        Seg_L.ChildPrice = seg_.CP;
        if (seg_.CPT != null) {
            Seg_L.ChildPriceT = seg_.CPT;
        }
        Seg_L.InfantPrice = seg_.IP;
        if (seg_.IPT != null) {
            Seg_L.InfantPriceT = seg_.IPT;
        }

        Seg_L.TotalTax = seg_.TT;
        Seg_L.TotalFare = seg_.TF;
        Seg_L.ttlDiscount = seg_.TTDIS;
        Seg_L.CancePenalty = seg_.CNP;
        Seg_L.ChangPenalty = seg_.CHP;
        Seg_L.Refundable = seg_.RF;
        Seg_L.RefundableIn = seg_.RFIN;
        Seg_L.SpecialSegKey = seg_.SSK;
        Seg_L.ConnType = seg_.CT;
        if (Seg_L.bonds[0].lstCanPo != null) {
            Seg_L.lstCanPo = Seg_L.bonds[0].lstCanPo;
        } else {
            Seg_L.lstCanPo = seg_.LCP;
        }
        //Seg_L.lstCanPo = seg_.LCP;
    }
    Seg_L.lstOutBound = [];
    Seg_L.lstInBound = [];

    Seg_L.IsHndBagg = seg_.IHB; //seg_.l_HB;
    if (seg_.Is_HBT != null) {
        Seg_L.IsHndBaggTp = seg_.Is_HBT;
    } else {
        Seg_L.IsHndBaggTp = isHndBGG; //seg_.l_HBT;
    }

    Seg_L.Note = seg_.Nt;
    Seg_L.CouponNote = seg_.CpNt;
    Seg_L.IsRoundTrip = seg_.I_RT;
    Seg_L.EngineId = seg_.EID;

    Seg_L.Saving = seg_.svg;
    Seg_L.Ssn = seg_.Ssn;
    Seg_L.Remark = seg_.Rmk;
    if (seg_.lstFr != null && seg_.lstFr.length > 0) {
        if (seg_.lstFr[fareId].TTDIS < seg_.lstFr[fareId].TF) {
            Seg_L.CouponCode = seg_.lstFr[fareId].CC;
        } else {
            Seg_L.CouponCode = "";
        }
    } else {
        Seg_L.CouponCode = seg_.CC;
    }
    if (Seg_L.CouponCode == "") {
        Seg_L.DiscountAmount = 0;
    }
    if (isRT_ && false) {
        Seg_L.CouponCode = "";
        Seg_L.CCL = "";
        Seg_L.IACL = "";
        Seg_L.CpnTxtS = "";
        Seg_L.CpnLstDis = 0;
    }
    Seg_L.VisaInfo = seg_.VI;
    Seg_L.SeatAvailablity = seg_.SeatAv;
    Seg_L.SearchOrigin = org;
    Seg_L.SearchDestination = des;
    Seg_L.listBrandfare = seg_.l_BF;
    Seg_L.IsBranded = seg_.I_BF;
    Seg_L.IsBrandeFareAvailabel = seg_.I_BFAv;
    Seg_L.FareTypeInd = seg_.FTpInd;

    if (seg_.FareRule != null) {
        Seg_L.FareRule = seg_.FareRule;
    }

    if (seg_.CBAMT != null) {
        Seg_L.CBAMT = seg_.CBAMT;
    }
    if (seg_.Comm != null) {
        Seg_L.Comm = seg_.Comm;
    }
    if (seg_.TDS != null) {
        Seg_L.TDS = seg_.TDS;
    }
    if (seg_.SF != null) {
        Seg_L.SF = seg_.SF;
    }
    try {
        Seg_L.IsFlightOutOfPolicy = seg_.IsFlightOutOfPolicy;
    } catch (e) {
        return Seg_L;
    }
    return JSON.stringify(Seg_L);
};
